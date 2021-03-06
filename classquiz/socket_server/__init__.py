#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json
import os

import aiohttp
import socketio

from typing import Any
from classquiz.config import redis, settings
from classquiz.db.models import PlayGame, QuizQuestionType
from pydantic import BaseModel, ValidationError

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=[])
settings = settings()


async def generate_final_results(game_data: PlayGame, game_pin: str) -> dict:
    results = {}
    for i in range(len(game_data.questions)):
        redis_res = await redis.get(f"game_session:{game_pin}:{i}")
        if redis_res is None:
            break
        else:
            results[str(i)] = json.loads(redis_res)
    return results


class _JoinGameData(BaseModel):
    username: str
    game_pin: str
    captcha: str | None


class _GameSessionPlayer(BaseModel):
    username: str
    sid: str


class _GameSession(BaseModel):
    admin: str
    game_id: str
    players: list[_GameSessionPlayer | None]
    answers: list[Any]


@sio.event
async def join_game(sid: str, data: dict):
    redis_res = await redis.get(f"game:{data['game_pin']}")
    if redis_res is None:
        await sio.emit("game_not_found", room=sid)
        return
    try:
        data = _JoinGameData(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)
        return
    # +++ START checking captcha +++
    async with aiohttp.ClientSession() as session:
        try:
            if json.loads(redis_res)["captcha_enabled"]:
                try:
                    async with session.post(
                        "https://hcaptcha.com/siteverify",
                        data={"response": data.captcha, "secret": settings.hcaptcha_key},
                    ) as resp:
                        resp_data = await resp.json()
                        if not resp_data["success"]:
                            print("CAPTCHA FAILED")
                            return
                except KeyError:
                    print("CAPTCHA FAILED")

                    return
        except TypeError:
            pass
    # --- END checking captcha ---
    session = {
        "game_pin": data.game_pin,
        "username": data.username,
        "admin": False,
    }
    await sio.save_session(sid, session)
    await sio.emit("joined_game", redis_res, room=sid)
    redis_res = await redis.get(f"game_session:{data.game_pin}")
    redis_res = _GameSession.parse_raw(redis_res)
    redis_res.players.append(_GameSessionPlayer(username=data.username, sid=sid))
    await redis.set(
        f"game_session:{data.game_pin}",
        _GameSession(admin=redis_res.admin, game_id=redis_res.game_id, players=redis_res.players, answers=[]).json(),
        ex=18000,
    )
    await sio.emit(
        "player_joined",
        {"username": data.username, "sid": sid},
        room=redis_res.admin,
    )
    sio.enter_room(sid, data.game_pin)


@sio.event
async def start_game(sid: str, _data: dict):
    session = await sio.get_session(sid)
    if session["admin"]:
        await sio.emit("start_game", room=session["game_pin"])


class _RegisterAsAdminData(BaseModel):
    game_pin: str
    game_id: str


@sio.event
async def register_as_admin(sid: str, data: dict):
    try:
        data = _RegisterAsAdminData(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)
        return
    game_pin = data.game_pin
    game_id = data.game_id
    if (await redis.get(f"game_session:{game_pin}")) is None:
        await redis.set(
            f"game_session:{game_pin}",
            _GameSession(admin=sid, game_id=game_id, answers=[], players=[]).json(),
            ex=18000,
        )

        await sio.emit(
            "registered_as_admin",
            {"game_id": game_id, "game": await redis.get(f"game:{game_pin}")},
            room=sid,
        )
        async with sio.session(sid) as session:
            session["game_pin"] = game_pin
            session["admin"] = True
        sio.enter_room(sid, game_pin)
    else:
        await sio.emit("already_registered_as_admin", room=sid)


@sio.event
async def get_question_results(sid: str, data: dict):
    session = await sio.get_session(sid)
    if session["admin"]:
        redis_res = await redis.get(f"game_session:{session['game_pin']}:{data['question_number']}")
        game_pin = session["game_pin"]
        await sio.emit("question_results", redis_res, room=game_pin)


@sio.event
async def set_question_number(sid, data: str):
    # data is just a number (as a str) of the question
    session = await sio.get_session(sid)
    if session["admin"]:
        game_pin = session["game_pin"]
        await sio.emit("set_question_number", data, room=game_pin)


class _SubmitAnswerData(BaseModel):
    question_index: int
    answer: str


class _AnswerData(BaseModel):
    username: str
    answer: str
    right: bool


class _AnswerDataList(BaseModel):
    # Just a method to make a top-level list
    __root__: list[_AnswerData]


@sio.event
async def submit_answer(sid: str, data: dict):
    try:
        data = _SubmitAnswerData(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)
        return
    session = await sio.get_session(sid)
    game_data = PlayGame.parse_raw(await redis.get(f"game:{session['game_pin']}"))
    answer_right = False
    if game_data.questions[int(data.question_index)].type == QuizQuestionType.ABCD:
        for answer in game_data.questions[int(data.question_index)].answers:
            if answer.answer == data.answer and answer.right:
                answer_right = True
                break
    elif game_data.questions[int(data.question_index)].type == QuizQuestionType.RANGE:
        if (
            game_data.questions[int(data.question_index)].answers.min_correct
            <= int(data.answer)
            <= game_data.questions[int(data.question_index)].answers.max_correct
        ):
            answer_right = True
    else:
        raise NotImplementedError
    answers = await redis.get(f"game_session:{session['game_pin']}:{data.question_index}")
    if answers is None:
        await redis.set(
            f"game_session:{session['game_pin']}:{data.question_index}",
            _AnswerDataList(
                __root__=[_AnswerData(username=session["username"], answer=data.answer, right=answer_right)]
            ).json(),
            ex=18000,
        )
    else:
        answers = _AnswerDataList.parse_raw(answers)
        answers.__root__.append(_AnswerData(username=session["username"], answer=data.answer, right=answer_right))
        await redis.set(
            f"game_session:{session['game_pin']}:{data.question_index}",
            answers.json(),
            ex=18000,
        )

    # await redis.set(f"game_data:{session['game_pin']}", json.dumps(data))


@sio.event
async def get_final_results(sid: str, _data: dict):
    session: dict = await sio.get_session(sid)
    game_data = PlayGame(**json.loads(await redis.get(f"game:{session['game_pin']}")))
    results = {}
    if not session["admin"]:
        return
    results = await generate_final_results(game_data, session["game_pin"])
    await sio.emit("final_results", results, room=session["game_pin"])


@sio.event
async def get_export_token(sid):
    session = await sio.get_session(sid)
    if not session["admin"]:
        return
    game_data = PlayGame(**json.loads(await redis.get(f"game:{session['game_pin']}")))
    results = await generate_final_results(game_data, session["game_pin"])
    token = os.urandom(32).hex()
    await redis.set(f"export_token:{token}", json.dumps(results))
    await sio.emit("export_token", token, room=sid)
