# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import enum
import typing
from datetime import datetime

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel, ValidationError
from classquiz.config import redis
from classquiz.db.models import PlayGame, QuizQuestionType, AnswerData, GamePlayer
from classquiz.socket_server import sio, calculate_score, set_answer

router = APIRouter()


class SubmitAnswerInput(BaseModel):
    answer: int


async def submit_answer_fn(data_answer: int, game_pin: str, player_id: str, now: datetime):
    redis_res_game = await redis.get(f"game:{game_pin}")
    username = await redis.get(f"game:cqc:player:{player_id}")
    if redis_res_game is None or username is None:
        raise HTTPException(status_code=404, detail="id not existent")
    game = PlayGame.parse_raw(redis_res_game)
    if not game.question_show:
        return

    question = game.questions[game.current_question]
    question_time = datetime.fromisoformat(await redis.get(f"game:{game_pin}:current_time"))
    try:
        selected_answer = question.answers[data_answer].answer
    except (KeyError, IndexError):
        return
    if await redis.get(f"answer_given:{player_id}:{game.current_question}") is not None:
        return
    answer_right = False
    if question.type == QuizQuestionType.ABCD:
        for answer in question.answers:
            if answer.answer == selected_answer and answer.right:
                answer_right = True
                break
    elif question.type == QuizQuestionType.VOTING:
        answer_right = False
    else:
        return
    diff = (question_time - now).total_seconds() * 1000
    score = 0
    if answer_right:
        score = calculate_score(abs(diff), int(float(question.time)))
    await redis.set(f"answer_given:{player_id}:{game.current_question}", "True", ex=600)
    await redis.hincrby(f"game_session:{game_pin}:player_scores", username, score)
    answer_data = AnswerData(
        username=username,
        answer=selected_answer,
        right=answer_right,
        time_taken=abs(diff),
        score=score,
    )
    answers = await redis.get(f"game_session:{game_pin}:{game.current_question}")
    answers = await set_answer(answers, game_pin=game_pin, data=answer_data, q_index=game.current_question)
    player_count = await redis.scard(f"game_session:{game_pin}:players")
    await sio.emit("player_answer", {})
    if answers is not None and len(answers.__root__) == player_count:
        await sio.emit("everyone_answered", {})


button_to_index_map = {"y": 0, "r": 3, "g": 1, "b": 2}


class WebSocketTypes(enum.Enum):
    ButtonPress = "bp"
    Error = "e"


class WebSocketRequest(BaseModel):
    type: WebSocketTypes
    data: typing.Any


wss_clients = {}


@router.websocket("/{game_id}")
async def websocket_endpoint(ws: WebSocket, game_id: str):
    try:
        if game_id in wss_clients:
            await ws.close(code=status.WS_1001_GOING_AWAY)
            print(f"Client {game_id} already exists.")
            return
        await ws.accept()
        wss_clients[game_id] = ws

        player_id, game_pin = game_id.split(":")
        if player_id is None or game_pin is None:
            await ws.send_text(WebSocketRequest(type=WebSocketTypes.Error, data="BadId").json())
            await ws.close(code=status.WS_1003_UNSUPPORTED_DATA)
        username = await redis.get(f"game:cqc:player:{player_id}")
        await sio.emit(
            "player_joined",
            {"username": username, "sid": None},
            room=f"admin:{game_pin}",
        )
        await redis.sadd(f"game_session:{game_pin}:players", GamePlayer(username=username, sid=None).json())

        while True:
            raw_data = await ws.receive_text()
            try:
                data = WebSocketRequest.parse_raw(raw_data)
            except ValidationError as e:
                print("ValError")
                print(e)
                print(raw_data)
                await ws.send_text(WebSocketRequest(type=WebSocketTypes.Error, data="ValidationError").json())
                continue

            if data.type == WebSocketTypes.ButtonPress:
                now = datetime.now()
                try:
                    answer_index = button_to_index_map[data.data.lower()]
                except (KeyError, AttributeError):
                    await ws.send_text(WebSocketRequest(type=WebSocketTypes.Error, data="InvalidButton").json())
                    continue
                await submit_answer_fn(answer_index, game_pin, player_id, now)

    except WebSocketDisconnect as ex:
        print(f"Client {game_id} is disconnected: {ex}")
        wss_clients.pop(game_id, None)
