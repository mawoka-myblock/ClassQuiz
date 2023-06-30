# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import json
import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from classquiz.config import settings, redis
from classquiz.db.models import (
    PlayGame,
    GamePlayer,
    GameAnswer1,
    GameAnswer2,
    GameSession,
    QuizQuestion,
    RangeQuizAnswer,
    ABCDQuizAnswer,
    QuizQuestionType,
    VotingQuizAnswer,
    AnswerDataList,
)
from classquiz.auth import check_api_key
from classquiz.socket_server import ReturnQuestion, sio

settings = settings()

router = APIRouter()


class _GetLiveDataPlayers(BaseModel):
    count: int | str


class _ABCDQuizAnswer(ABCDQuizAnswer):
    color_code: str


class _QuizQuestion(QuizQuestion):
    answers: list[ABCDQuizAnswer] | RangeQuizAnswer | list[VotingQuizAnswer]

    @validator("answers")
    def answers_not_none_if_abcd_type(cls, v, values):
        # if values["type"] == QuizQuestionType.ABCD and type(v[0]) != _ABCDQuizAnswer:
        #     print(type(v[0]), values)
        #     raise ValueError("Answers can't be none if type is ABCD")
        # if values["type"] == QuizQuestionType.RANGE and type(v) != RangeQuizAnswer:
        #     raise ValueError("Answer must be from type RangeQuizAnswer if type is RANGE")
        # if values["type"] == QuizQuestionType.VOTING and type(v[0]) != VotingQuizAnswer:
        #     raise ValueError("Answer must be from type VotingQuizAnswer if type is VOTING")
        # return v
        return v


class _PlayGame(PlayGame):
    questions: list[_QuizQuestion]


class _GetLivePlayGame(_PlayGame):
    total_questions: int


class GetLiveDataResponse(BaseModel):
    quiz: _GetLivePlayGame
    data: GameSession
    players: _GetLiveDataPlayers


@router.get("/")
async def get_live_game_data(
    game_pin: str,
    api_key: str,
    player_count_as_a_string: bool = False,
    in_array: bool = False,
    in_human_count: bool = False,
):
    user_id = await check_api_key(api_key)
    redis_res = await redis.get(f"game:{game_pin}")
    if redis_res is None:
        game_pin = await redis.get(f"game_pin:{user_id}:{game_pin}")
        redis_res = await redis.get(f"game:{game_pin}")
    if redis_res is None or user_id is None:
        raise HTTPException(status_code=404, detail="Game not found or API key not found")
    game = _PlayGame.parse_raw(redis_res)
    if game.user_id != user_id:
        raise HTTPException(status_code=404, detail="Game not found or API key not found")
    for i, question in enumerate(game.questions):
        if question.type == QuizQuestionType.ABCD:
            for o, answer in enumerate(question.answers):
                color = "#00F007"
                try:
                    if not answer.right:
                        color = "#FF0000"
                except AttributeError:
                    game.questions[i].answers[o] = VotingQuizAnswer(
                        answer=answer.answer, color=answer.color, image=answer.image
                    )
                    continue
                game.questions[i].answers[o] = _ABCDQuizAnswer(
                    right=answer.right, answer=answer.answer, color=answer.color, color_code=color
                )

    data_redis_res = await redis.get(f"game_session:{game_pin}")
    if data_redis_res is None:
        raise HTTPException(status_code=404, detail="Game not found or API key not found")
    data = GameSession.parse_raw(data_redis_res)
    for i in range(0, len(game.questions)):
        res = await redis.get(f"game_session:{game_pin}:{i}")
        if res is None:
            break
        else:
            res = json.loads(res)
            ga_1 = GameAnswer1(id=i, answers=[GameAnswer2.parse_obj(i) for i in res])
            data.answers.append(ga_1)
    player_count = await redis.scard(f"game_session:{game_pin}:players")
    total_questions = len(game.questions)
    game = _GetLivePlayGame(**{**game.dict(), "total_questions": total_questions})
    if in_human_count:
        game.current_question += 1

    return_obj = None
    if player_count_as_a_string:
        return_obj = GetLiveDataResponse(quiz=game, data=data, players=_GetLiveDataPlayers(count=str(player_count)))
    else:
        return_obj = GetLiveDataResponse(quiz=game, data=data, players=_GetLiveDataPlayers(count=player_count))

    if in_array:
        return [return_obj]
    else:
        return return_obj


@router.get("/user_count")
async def get_game_user_count(game_pin: str, api_key: str, as_string: bool = False, as_array: bool = False):
    user_id = await check_api_key(api_key)
    redis_res = await redis.get(f"game_session:{game_pin}")
    if redis_res is None:
        game_pin = await redis.get(f"game_pin:{user_id}:{game_pin}")
    player_count = await redis.scard(f"game_session:{game_pin}:players")
    if as_string:
        player_count = str(player_count)
    if as_array:
        return [{"players": {"count": player_count}}]
    else:
        return {"players": {"count": player_count}}


@router.get(
    "/players",
)
async def get_game_session(game_pin: str, api_key: str | None = None, game_id: uuid.UUID | None = None):
    if game_id is None and api_key is None:
        raise HTTPException(status_code=401, detail="API-Key and Quiz-ID are missing")
    user_id = await check_api_key(api_key)
    redis_res = await redis.get(f"game_session:{game_pin}")
    if redis_res is None:
        game_pin = await redis.get(f"game_pin:{user_id}:{game_pin}")
        redis_res = await redis.get(f"game_session:{game_pin}")
    if redis_res is None:
        raise HTTPException(status_code=404, detail="Game not found or API key not found")
    data = GameSession.parse_raw(redis_res)
    if user_id is None and data.game_id != str(game_id):
        raise HTTPException(status_code=401, detail="Game not found or API key not found")
    game = PlayGame.parse_raw(await redis.get(f"game:{game_pin}"))
    if game.user_id != user_id and data.game_id != str(game_id):
        raise HTTPException(status_code=404, detail="Game not found or API key not found")
    for i in range(0, len(game.questions)):
        res = await redis.get(f"game_session:{game_pin}:{i}")
        if res is None:
            break
        else:
            res = json.loads(res)
            ga_1 = GameAnswer1(id=i, answers=[GameAnswer2.parse_obj(i) for i in res])
            data.answers.append(ga_1)
    players = await redis.smembers(f"game_session:{game_pin}:players")
    player_list = []
    for p in players:
        player_list.append(GamePlayer.parse_raw(p))
    return player_list


@router.post("/set_question")
async def set_next_question(game_pin: str, question_number: int, api_key: str):
    user_id = await check_api_key(api_key)
    redis_res = await redis.get(f"game:{game_pin}")
    if redis_res is None:
        game_pin = await redis.get(f"game_pin:{user_id}:{game_pin}")
        redis_res = await redis.get(f"game:{game_pin}")
    if redis_res is None or user_id is None:
        raise HTTPException(status_code=404, detail="Game not found or API key not found")
    game_data = PlayGame.parse_raw(redis_res)
    if game_data.user_id != user_id:
        raise HTTPException(status_code=404, detail="Game not found or API key not found")
    game_data.current_question = question_number
    await redis.set(f"game:{game_pin}", game_data.json(), ex=18000)
    await sio.emit(
        "set_question_number",
        {
            "question_index": question_number,
            "question": ReturnQuestion(**game_data.dict(include={"questions"})["questions"][question_number]).dict(),
        },
        room=game_pin,
    )


@router.get("/scores")
async def get_live_player_scores(game_pin: str, api_key: str):
    user_id = await check_api_key(api_key)
    redis_res = await redis.get(f"game:{game_pin}")
    if redis_res is None:
        game_pin = await redis.get(f"game_pin:{user_id}:{game_pin}")
        redis_res = await redis.get(f"game:{game_pin}")
    if redis_res is None or user_id is None:
        raise HTTPException(status_code=404, detail="Game not found or API key not found")
    res = await redis.hgetall(f"game_session:{game_pin}:player_scores")
    return_arr = []
    for username in res:
        return_arr.append({"username": username, "score": int(res[username])})
    return_arr = sorted(return_arr, key=lambda d: d["score"], reverse=True)
    return return_arr


@router.get("/get_question/now")
async def too_stupid_to_come_up_with_a_name(game_pin: str, api_key: str, in_human_count: bool = False):
    user_id = await check_api_key(api_key)
    redis_res = await redis.get(f"game:{game_pin}")
    if redis_res is None:
        game_pin = await redis.get(f"game_pin:{user_id}:{game_pin}")
        redis_res = await redis.get(f"game:{game_pin}")
    if redis_res is None or user_id is None:
        raise HTTPException(status_code=404, detail="Game not found or API key not found")
    game = PlayGame.parse_raw(redis_res)
    for i, question in enumerate(game.questions):
        if question.type == QuizQuestionType.ABCD:
            for o, answer in enumerate(question.answers):
                color = "#00F007"
                if not answer.right:
                    color = "#FF0000"
                game.questions[i].answers[o] = _ABCDQuizAnswer(
                    right=answer.right, answer=answer.answer, color=answer.color, color_code=color
                )
    if game.current_question >= 0:
        return [
            {
                **game.questions[game.current_question].dict(),
                "current_question": game.current_question + 1 if in_human_count else game.current_question,
                "total_questions": len(game.questions),
            }
        ]
    else:
        game.current_question += 1
        return [{"question": {}, "current_question": game.current_question, "total_questions": len(game.questions)}]


@router.get("/voting")
async def voting_results(game_pin: str, api_key: str, as_array: bool = False):
    user_id = await check_api_key(api_key)
    redis_res = await redis.get(f"game:{game_pin}")
    if redis_res is None:
        game_pin = await redis.get(f"game_pin:{user_id}:{game_pin}")
        redis_res = await redis.get(f"game:{game_pin}")
    if redis_res is None or user_id is None:
        raise HTTPException(status_code=404, detail="Game not found or API key not found")
    game = PlayGame.parse_raw(redis_res)
    if game.questions[game.current_question].type != QuizQuestionType.VOTING:
        return
    answer_data = await redis.get(f"game_session:{game_pin}:{game.current_question}")
    if answer_data is None:
        return
    answer_list = AnswerDataList.parse_raw(answer_data)
    answer_dict = {}
    for answer in game.questions[game.current_question].answers:
        answer_dict[answer.answer] = 0
    for answer in answer_list.__root__:
        answer_dict[answer.answer] += 1
    if as_array:
        return [answer_dict]
    else:
        return answer_dict
