import json
import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from classquiz.config import redis
import pydantic

from classquiz.auth import get_current_user, get_current_user_optional
from classquiz.db.models import Quiz, QuizInput, User, PlayGame
from random import randint
import uuid

router = APIRouter()


@router.post("/create")
async def create_quiz_lol(quiz_input: QuizInput, user: User = Depends(get_current_user)):
    quiz = Quiz(**quiz_input.dict(), user_id=user.id)
    return await quiz.save()


@router.get("/get/{quiz_id}")
async def get_quiz_from_id(quiz_id: str, user: User | None = Depends(get_current_user_optional)):
    try:
        quiz_id = uuid.UUID(quiz_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="badly formed quiz id")
    if user is None:
        quiz = await Quiz.objects.get_or_none(id=quiz_id, public=True)
    else:
        quiz = await Quiz.objects.get_or_none(id=quiz_id, public=False, user_id=user.id)
    if quiz is None:
        return JSONResponse(status_code=404, content={"detail": "quiz not found"})
    else:
        return quiz


@router.post("/start/{quiz_id}")
async def start_quiz(quiz_id: str, user: User = Depends(get_current_user)):
    try:
        quiz_id = uuid.UUID(quiz_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="badly formed quiz id")
    quiz = await Quiz.objects.get_or_none(id=quiz_id, public=False, user_id=user.id)
    if quiz is None:
        return JSONResponse(status_code=404, content={"detail": "quiz not found"})
    else:
        game_pin = randint(10000000, 99999999)
        game = PlayGame(quiz_id=quiz_id, game_pin=str(game_pin), questions=quiz.questions, game_id=uuid.uuid4(),
                        title=quiz.title, description=quiz.description)
        await redis.set(f"game:{str(game.game_pin)}", (game.json()), ex=18000)
        return {**quiz.dict(exclude={"id"}), **game.dict(exclude={"questions"})}


@router.get("/join/{game_pin}")
async def get_game_id(game_pin: str):
    redis_res = (await redis.get(f"game:{game_pin}")).decode()
    if redis_res is None:
        raise HTTPException(status_code=404, detail="game not found")
    else:
        return json.loads(redis_res)["game_id"]


@router.get("/list")
async def get_quiz_list(user: User = Depends(get_current_user)):
    return await Quiz.objects.filter(user_id=user.id).all()
