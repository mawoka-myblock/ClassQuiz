#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import base64
import hashlib
import json
import os

import aiohttp
import socketio
from cryptography.fernet import Fernet

from classquiz.config import redis, settings
from classquiz.db.models import PlayGame, QuizQuestionType, GameSession, GamePlayer, QuizQuestion, VotingQuizAnswer
from pydantic import BaseModel, ValidationError, validator
from datetime import datetime

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=[])
settings = settings()


def get_fernet_key() -> bytes:
    hlib = hashlib.sha256()
    hlib.update(settings.secret_key.encode("utf-8"))
    return base64.urlsafe_b64encode(hlib.hexdigest().encode("latin-1")[:32])


fernet = Fernet(get_fernet_key())


async def generate_final_results(game_data: PlayGame, game_pin: str) -> dict:
    results = {}
    for i in range(len(game_data.questions)):
        redis_res = await redis.get(f"game_session:{game_pin}:{i}")
        if redis_res is None:
            continue
        else:
            results[str(i)] = json.loads(redis_res)
    return results


class _JoinGameData(BaseModel):
    username: str
    game_pin: str
    captcha: str | None


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
    game_data = PlayGame.parse_raw(redis_res)
    if game_data.started:
        await sio.emit("game_already_started", room=sid)
        return
    # +++ START checking captcha +++
    async with aiohttp.ClientSession() as session:
        try:
            if game_data.captcha_enabled:
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
    if await redis.get(f"game_session:{data.game_pin}:players:{data.username}") is not None:
        await sio.emit("username_already_exists", room=sid)
        return

    session = {
        "game_pin": data.game_pin,
        "username": data.username,
        "admin": False,
    }
    await sio.save_session(sid, session)
    await sio.emit(
        "joined_game",
        {
            **json.loads(game_data.json(exclude={"quiz_id", "questions", "user_id"})),
            "question_count": len(game_data.questions),
        },
        room=sid,
    )
    redis_res = await redis.get(f"game_session:{data.game_pin}")
    redis_res = GameSession.parse_raw(redis_res)
    await redis.set(f"game_session:{data.game_pin}:players:{data.username}", sid, ex=18000)
    await redis.sadd(f"game_session:{data.game_pin}:players", GamePlayer(username=data.username, sid=sid).json())
    # await redis.set(
    #     f"game_session:{data.game_pin}",
    #     GameSession(admin=redis_res.admin, game_id=redis_res.game_id, answers=[]).json(),
    #     ex=18000,
    # )
    await sio.emit(
        "player_joined",
        {"username": data.username, "sid": sid},
        room=redis_res.admin,
    )
    # +++ Time-Sync +++
    encrypted_datetime = fernet.encrypt(datetime.now().isoformat().encode("utf-8")).decode("utf-8")
    await sio.emit("time_sync", encrypted_datetime, room=sid)
    # --- Time-Sync ---
    sio.enter_room(sid, data.game_pin)


@sio.event
async def start_game(sid: str, _data: dict):
    session = await sio.get_session(sid)
    if session["admin"]:
        game_data = PlayGame.parse_raw(await redis.get(f"game:{session['game_pin']}"))
        game_data.started = True
        await redis.set(f"game:{session['game_pin']}", game_data.json())
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
            GameSession(admin=sid, game_id=game_id, answers=[]).json(),
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


class ABCDQuizAnswerWithoutSolution(BaseModel):
    answer: str
    color: str | None


class RangeQuizAnswerWithoutSolution(BaseModel):
    min: int
    max: int


class ReturnQuestion(QuizQuestion):
    answers: list[ABCDQuizAnswerWithoutSolution] | RangeQuizAnswerWithoutSolution | list[VotingQuizAnswer]

    @validator("answers")
    def answers_not_none_if_abcd_type(cls, v, values):
        if values["type"] == QuizQuestionType.ABCD and type(v[0]) != ABCDQuizAnswerWithoutSolution:
            raise ValueError("Answers can't be none if type is ABCD")
        if values["type"] == QuizQuestionType.RANGE and type(v) != RangeQuizAnswerWithoutSolution:
            raise ValueError("Answer must be from type RangeQuizAnswer if type is RANGE")
        if values["type"] == QuizQuestionType.VOTING and type(v[0]) != VotingQuizAnswer:
            # print("Answer must be from type VotingQuizAnswer if type is VOTING")
            pass
        return v


@sio.event
async def set_question_number(sid, data: str):
    # data is just a number (as a str) of the question
    session = await sio.get_session(sid)
    if session["admin"]:
        game_pin = session["game_pin"]
        game_data = PlayGame.parse_raw(await redis.get(f"game:{session['game_pin']}"))
        game_data.current_question = int(float(data))
        await redis.set(f"game:{session['game_pin']}", game_data.json())
        await redis.set(f"game:{session['game_pin']}:current_time", datetime.now().isoformat())
        temp_return = game_data.dict(include={"questions"})["questions"][int(float(data))]
        if game_data.questions[int(float(data))].type == QuizQuestionType.VOTING:
            for i in range(len(temp_return["answers"])):
                temp_return["answers"][i] = VotingQuizAnswer(**temp_return["answers"][i])
        await sio.emit(
            "set_question_number",
            {
                "question_index": int(float(data)),
                "question": ReturnQuestion(**temp_return).dict(),
            },
            room=game_pin,
        )


class _SubmitAnswerData(BaseModel):
    question_index: int
    answer: str


class _AnswerData(BaseModel):
    username: str
    answer: str
    right: bool
    time_taken: float  # In milliseconds
    score: int


class _AnswerDataList(BaseModel):
    # Just a method to make a top-level list
    __root__: list[_AnswerData]


@sio.event
async def submit_answer(sid: str, data: dict):
    now = datetime.now()
    try:
        data = _SubmitAnswerData(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)
        return
    session = await sio.get_session(sid)
    game_data = PlayGame.parse_raw(await redis.get(f"game:{session['game_pin']}"))
    answer_right = False
    if game_data.questions[int(float(data.question_index))].type == QuizQuestionType.ABCD:
        for answer in game_data.questions[int(float(data.question_index))].answers:
            if answer.answer == data.answer and answer.right:
                answer_right = True
                break
    elif game_data.questions[int(float(data.question_index))].type == QuizQuestionType.RANGE:
        if (
            game_data.questions[int(float(data.question_index))].answers.min_correct
            <= int(float(data.answer))
            <= game_data.questions[int(float(data.question_index))].answers.max_correct
        ):
            answer_right = True
    elif game_data.questions[int(float(data.question_index))].type == QuizQuestionType.VOTING:
        answer_right = False
    else:
        raise NotImplementedError
    latency = int(float((await sio.get_session(sid))["ping"]))
    time_q_started = datetime.fromisoformat(await redis.get(f"game:{session['game_pin']}:current_time"))
    answers = await redis.get(f"game_session:{session['game_pin']}:{data.question_index}")
    diff = (time_q_started - now).total_seconds() * 1000  # - timedelta(milliseconds=latency)

    # print(abs(diff) - latency, latency, abs(diff))
    def calculate_score(z: float, t: int) -> int:
        t = t * 1000
        res = (t - z) / t
        return int(res * 1000)

    score = 0
    if answer_right:
        score = calculate_score(
            abs(diff) - latency, int(float(game_data.questions[int(float(data.question_index))].time))
        )
    await redis.hincrby(f"game_session:{session['game_pin']}:player_scores", session["username"], score)
    if answers is None:
        await redis.set(
            f"game_session:{session['game_pin']}:{data.question_index}",
            _AnswerDataList(
                __root__=[
                    _AnswerData(
                        username=session["username"],
                        answer=data.answer,
                        right=answer_right,
                        time_taken=abs(diff) - latency,
                        score=score,
                    )
                ]
            ).json(),
            ex=18000,
        )
    else:
        answers = _AnswerDataList.parse_raw(answers)
        answers.__root__.append(
            _AnswerData(
                username=session["username"],
                answer=data.answer,
                right=answer_right,
                time_taken=abs(diff) - latency,
                score=score,
            )
        )
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


@sio.event
async def show_solutions(sid: str, _data: dict):
    session: dict = await sio.get_session(sid)
    game_data = PlayGame(**json.loads(await redis.get(f"game:{session['game_pin']}")))
    if not session["admin"]:
        return
    await sio.emit("solutions", game_data.questions[game_data.current_question].dict(), room=session["game_pin"])


@sio.event
async def echo_time_sync(sid: str, data: str):
    then_dec = fernet.decrypt(data).decode("utf-8")
    then = datetime.fromisoformat(then_dec)
    now = datetime.now()
    delta = now - then
    async with sio.session(sid) as session:
        session["ping"] = delta.microseconds / 1000


class _KickPlayerInput(BaseModel):
    username: str


@sio.event
async def kick_player(sid: str, data: dict):
    try:
        data = _KickPlayerInput(**data)
    except ValidationError as e:
        await sio.emit("error", room=sid)
        print(e)
        return

    session: dict = await sio.get_session(sid)
    if not session["admin"]:
        return

    player_sid = await redis.get(f"game_session:{session['game_pin']}:players:{data.username}")
    await redis.spop(f"game_session:{session['game_pin']}:players", GamePlayer(username=data.username, sid=sid).json())
    sio.leave_room(player_sid, session["game_pin"])
    await sio.emit("kick", room=player_sid)
