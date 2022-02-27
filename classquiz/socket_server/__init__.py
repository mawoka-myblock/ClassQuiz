import socketio
import json
from classquiz.config import redis
from classquiz.db.models import GameSession, GameAnser1, GameAnser2, PlayGame
from redis.commands.json.path import Path

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


@sio.event
async def connect(sid, environ, lol):
    print(sid, "connected")


# sio.enter_room(sid, lol)
# print(lol)
# print(environ["asgi.scope"]["headers"])
# print(environ)
# async with sio.session(sid) as session:
#    session['username'] = "username"


@sio.event
async def join_game(sid, data):
    print(sid, data, "JOIN_GAME")
    redis_res = await redis.get(f"game:{data['game_pin']}")
    if redis_res is None:
        await sio.emit("game_not_found", room=sid)
    else:
        session = {'game_pin': data["game_pin"], "username": data["username"], "admin": False}
        await sio.save_session(sid, session)
        await sio.emit("joined_game", redis_res, room=sid)
        redis_res = (await redis.get(f"game_session:{data['game_pin']}"))
        redis_res = json.loads(redis_res)
        print(redis_res)
        redis_res["players"].append({"username": data["username"], "sid": sid})
        await redis.set(f"game_session:{data['game_pin']}",
                        json.dumps({"admin": redis_res["admin"], "game_id": redis_res["game_id"],
                                    "players": redis_res["players"], "answers": []}))
        await sio.emit("player_joined", {"username": data["username"], "sid": sid}, room=redis_res["admin"])
        sio.enter_room(sid, data["game_pin"])  # TODO: make more secure


@sio.event
async def start_game(sid, data):
    print(sid, data, "START_GAME")
    session = await sio.get_session(sid)
    print(session)
    if session["admin"]:
        await sio.emit("start_game", room=session["game_pin"])


@sio.event
async def register_as_admin(sid, data):
    game_pin = data["game_pin"]
    game_id = data["game_id"]
    if (await redis.get(f"game_session:{game_pin}")) is None:
        await redis.set(f"game_session:{game_pin}", json.dumps({"admin": sid, "game_id": game_id, "players": []}))

        await sio.emit("registered_as_admin", {"game_id": game_id, "game": await redis.get(f"game:{data['game_pin']}")},
                       room=sid)
        async with sio.session(sid) as session:
            session['game_pin'] = data["game_pin"]
            session["admin"] = True
        sio.enter_room(sid, data["game_pin"])
    else:
        await sio.emit("already_registered_as_admin", room=sid)


@sio.event
async def get_question_results(sid, data):
    session = await sio.get_session(sid)
    if session["admin"]:
        redis_res = await redis.get(f"game_session:{session['game_pin']}:{data['question_number']}")
        game_pin = session['game_pin']
        await sio.emit("question_results", redis_res, room=game_pin)


@sio.event
async def set_question_number(sid, data):
    session = await sio.get_session(sid)
    if session["admin"]:
        game_pin = session['game_pin']
        await sio.emit("set_question_number", data, room=game_pin)


@sio.event
async def submit_answer(sid, data):
    session = await sio.get_session(sid)
    redis_res = await redis.get(f"game_session:{session['game_pin']}")
    game_session = GameSession(**json.loads(redis_res))
    game_data = PlayGame(**json.loads(await redis.get(f"game:{session['game_pin']}")))
    print(game_session)
    answer_right = False
    for answer in game_data.questions[int(data["question_index"])].answers:
        if answer.answer == data["answer"] and answer.right:
            answer_right = True
            break
    answers = await redis.get(f"game_session:{session['game_pin']}:{data['question_index']}")
    if answers is None:
        await redis.set(f"game_session:{session['game_pin']}:{data['question_index']}",
                        json.dumps(
                            [{"username": session["username"], "answer": data["answer"], "right": answer_right}]))
    else:
        answers = json.loads(answers)
        answers.append({session["username"]: data["answer"]})
        await redis.set(f"game_session:{session['game_pin']}:{data['question_index']}", json.dumps(answers))

    # await redis.set(f"game_data:{session['game_pin']}", json.dumps(data))


# @sio.event
# async def admin_game(sid, data):
#     redis_res = await redis.get(f"game:{data['game_pin']}")
#     if redis_res is None:
#         await sio.emit("game_not_found", room=sid)
#     else:
#
#         await sio.emit("joined_game", data, room=data['game_pin'])


# @sio.event
# async def start_game(sid, data):
#     game_pin = (await sio.get_session(sid))['game_pin']
#     session = await sio.get_session(sid)
#     if session['admin']:
#         await sio.emit("start_game", data, room=game_pin)


@sio.event
async def get_game_data(sid, data):
    game_pin = (await sio.get_session(sid))['game_pin']
    game_data = await redis.get(f"game:{game_pin}")
    if game_data is not None:
        await sio.emit("game_data", json.loads(game_data), room=game_pin)
    print(sid, data, "GET_GAME_DATA")

#
# @sio.event
# async def message(sid, data):
#     game_pin = (await sio.get_session(sid))['game_pin']
#     await sio.emit("message", data, room=game_pin)
#
#
# @sio.on('*')
# async def catch_all(event, sid, data):
#     print(event, sid, data)
