import json

import aiohttp
import socketio

from classquiz.config import redis, settings
from classquiz.db.models import PlayGame

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=[])
settings = settings()


@sio.event
async def join_game(sid, data):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                "https://hcaptcha.com/siteverify",
                data={"response": data["captcha"], "secret": settings.hcaptcha_key},
            ) as resp:
                resp_data = await resp.json()
                if not resp_data["success"]:
                    print("CAPTCHA FAILED")
                    return
        except KeyError:
            print("CAPTCHA FAILED")
            return
    redis_res = await redis.get(f"game:{data['game_pin']}")
    if redis_res is None:
        await sio.emit("game_not_found", room=sid)
    else:
        session = {
            "game_pin": data["game_pin"],
            "username": data["username"],
            "admin": False,
        }
        await sio.save_session(sid, session)
        await sio.emit("joined_game", redis_res, room=sid)
        redis_res = await redis.get(f"game_session:{data['game_pin']}")
        redis_res = json.loads(redis_res)
        # print(redis_res)
        redis_res["players"].append({"username": data["username"], "sid": sid})
        await redis.set(
            f"game_session:{data['game_pin']}",
            json.dumps(
                {
                    "admin": redis_res["admin"],
                    "game_id": redis_res["game_id"],
                    "players": redis_res["players"],
                    "answers": [],
                }
            ),
            ex=18000,
        )
        await sio.emit(
            "player_joined",
            {"username": data["username"], "sid": sid},
            room=redis_res["admin"],
        )
        sio.enter_room(sid, data["game_pin"])  # TODO: make more secure


@sio.event
async def start_game(sid, _data):
    # print(sid, data, "START_GAME")
    session = await sio.get_session(sid)
    # print(session)
    if session["admin"]:
        await sio.emit("start_game", room=session["game_pin"])


@sio.event
async def register_as_admin(sid, data):
    game_pin = data["game_pin"]
    game_id = data["game_id"]
    if (await redis.get(f"game_session:{game_pin}")) is None:
        await redis.set(
            f"game_session:{game_pin}",
            json.dumps({"admin": sid, "game_id": game_id, "players": []}),
            ex=18000,
        )

        await sio.emit(
            "registered_as_admin",
            {"game_id": game_id, "game": await redis.get(f"game:{data['game_pin']}")},
            room=sid,
        )
        async with sio.session(sid) as session:
            session["game_pin"] = data["game_pin"]
            session["admin"] = True
        sio.enter_room(sid, data["game_pin"])
    else:
        await sio.emit("already_registered_as_admin", room=sid)


@sio.event
async def get_question_results(sid, data):
    session = await sio.get_session(sid)
    if session["admin"]:
        redis_res = await redis.get(f"game_session:{session['game_pin']}:{data['question_number']}")
        game_pin = session["game_pin"]
        await sio.emit("question_results", redis_res, room=game_pin)


@sio.event
async def set_question_number(sid, data):
    session = await sio.get_session(sid)
    if session["admin"]:
        game_pin = session["game_pin"]
        await sio.emit("set_question_number", data, room=game_pin)


@sio.event
async def submit_answer(sid, data):
    session = await sio.get_session(sid)
    # redis_res = await redis.get(f"game_session:{session['game_pin']}")
    # game_session = GameSession(**json.loads(redis_res))
    game_data = PlayGame(**json.loads(await redis.get(f"game:{session['game_pin']}")))
    # print(game_session)
    answer_right = False
    for answer in game_data.questions[int(data["question_index"])].answers:
        if answer.answer == data["answer"] and answer.right:
            answer_right = True
            break
    answers = await redis.get(f"game_session:{session['game_pin']}:{data['question_index']}")
    if answers is None:
        await redis.set(
            f"game_session:{session['game_pin']}:{data['question_index']}",
            json.dumps(
                [
                    {
                        "username": session["username"],
                        "answer": data["answer"],
                        "right": answer_right,
                    }
                ]
            ),
            ex=18000,
        )
    else:
        answers = json.loads(answers)
        answers.append(
            {
                "username": session["username"],
                "answer": data["answer"],
                "right": answer_right,
            }
        )
        await redis.set(
            f"game_session:{session['game_pin']}:{data['question_index']}",
            json.dumps(answers),
            ex=18000,
        )

    # await redis.set(f"game_data:{session['game_pin']}", json.dumps(data))


@sio.event
async def get_final_results(sid, _data):
    session = await sio.get_session(sid)
    game_data = PlayGame(**json.loads(await redis.get(f"game:{session['game_pin']}")))
    results = {}
    if not session["admin"]:
        return
    for i in range(len(game_data.questions)):
        redis_res = await redis.get(f"game_session:{session['game_pin']}:{i}")
        if redis_res is None:
            break
        else:
            results[str(i)] = json.loads(redis_res)
    await sio.emit("final_results", results, room=session["game_pin"])
