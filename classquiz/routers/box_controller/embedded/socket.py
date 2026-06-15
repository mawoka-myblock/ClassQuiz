# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import enum
import typing
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel, ValidationError

from classquiz.config import redis
from classquiz.db.models import AnswerData, GamePlayer, PlayGame, QuizQuestionType
from classquiz.socket_server import calculate_score, set_answer, sio
from classquiz.socket_server.helpers import check_answer, has_already_answered
from classquiz.socket_server.models import SubmitAnswerData

router = APIRouter()


async def submit_answer_fn(data_answer: int, game_pin: str, player_id: str, now: datetime):
    print(data_answer)
    game = await PlayGame.get_from_redis(game_pin)
    if not game.question_show:
        print("Not showing q")
        return

    question = game.questions[game.current_question]
    question_time = datetime.fromisoformat(await redis.get(f"game:{game_pin}:current_time"))
    username = await redis.get(f"game:cqc:player:{player_id}")
    already_answered = await has_already_answered(game_pin, game.current_question, username)
    if already_answered:
        print("already answerered")
        return
    if question.type not in (QuizQuestionType.ABCD, QuizQuestionType.VOTING):
        print("Wrong q type")
        return
    selected_answer = question.answers[data_answer].answer

    answer_data_obj = SubmitAnswerData(question_index=game.current_question, answer=selected_answer)
    answer_right, stored_answer = check_answer(game, answer_data_obj)
    diff = (question_time - now).total_seconds() * 1000
    score = 0
    if answer_right:
        score = calculate_score(
            abs(diff),
            int(float(question.time)),
        )
        if score > 1000:
            score = 1000
    await redis.set(f"answer_given:{player_id}:{game.current_question}", "True", ex=600)
    await redis.hincrby(f"game_session:{game_pin}:player_scores", username, score)
    answer_data = AnswerData(
        username=username,
        answer=stored_answer,
        right=answer_right,
        time_taken=abs(diff),
        score=score,
    )
    answers = await redis.get(f"game_session:{game_pin}:{game.current_question}")
    answers = await set_answer(answers, game_pin=game_pin, data=answer_data, q_index=game.current_question)
    player_count = await redis.scard(f"game_session:{game_pin}:players")
    await sio.emit("player_answer", {})
    if len(answers) == player_count:
        game.question_show = False
        await game.save(game_pin)
        await sio.emit("everyone_answered", {})


button_to_index_map = {"b": 0, "y": 1, "g": 2, "r": 3}


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
            await ws.send_text(WebSocketRequest(type=WebSocketTypes.Error, data="BadId").model_dump_json())
            await ws.close(code=status.WS_1003_UNSUPPORTED_DATA)
        username = await redis.get(f"game:cqc:player:{player_id}")
        await sio.emit(
            "player_joined",
            {"username": username, "sid": None},
            room=f"admin:{game_pin}",
        )
        await redis.sadd(
            f"game_session:{game_pin}:players",
            GamePlayer(username=username, sid=None).model_dump_json(),
        )

        while True:
            raw_data = await ws.receive_text()
            try:
                data = WebSocketRequest.model_validate_json(raw_data)
            except ValidationError as e:
                print("ValError")
                print(e)
                print(raw_data)
                await ws.send_text(
                    WebSocketRequest(type=WebSocketTypes.Error, data="ValidationError").model_dump_json()
                )
                continue

            if data.type == WebSocketTypes.ButtonPress:
                print("submitting")
                now = datetime.now()
                try:
                    answer_index = button_to_index_map[data.data.lower()]
                except (KeyError, AttributeError):
                    await ws.send_text(
                        WebSocketRequest(type=WebSocketTypes.Error, data="InvalidButton").model_dump_json()
                    )
                    continue
                await submit_answer_fn(answer_index, game_pin, player_id, now)

    except WebSocketDisconnect as ex:
        print(f"Client {game_id} is disconnected: {ex}")
        wss_clients.pop(game_id, None)
