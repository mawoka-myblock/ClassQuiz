import json
import uuid
from datetime import datetime
from random import randint

from pydantic import ValidationError

from classquiz.kahoot_importer.import_quiz import import_quiz
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import re

from classquiz.auth import get_current_user, get_current_user_optional
from classquiz.config import redis, settings, storage
from classquiz.db.models import Quiz, QuizInput, User, PlayGame

settings = settings()

router = APIRouter()


@router.post("/create")
async def create_quiz_lol(quiz_input: QuizInput, user: User = Depends(get_current_user)):
    imgur_regex = r"^https://i\.imgur\.com\/.{7}.(jpg|png|gif)$"
    server_regex = rf"^{settings.root_address}/api/v1/storage/download/.{36}--.{36}$"
    for question in quiz_input.questions:
        if question.image is not None:
            if not re.match(imgur_regex, question.image) or not re.match(server_regex, question.image):
                raise HTTPException(status_code=400, detail="image url is not valid")
    quiz = Quiz(**quiz_input.dict(), user_id=user.id, id=uuid.uuid4())
    await redis.delete("global_quiz_count")
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
        quiz = await Quiz.objects.get_or_none(id=quiz_id, user_id=user.id)
    if quiz is None:
        public_quiz = await Quiz.objects.get_or_none(id=quiz_id, public=True)
        if public_quiz is None:
            return JSONResponse(status_code=404, content={"detail": "quiz not found"})
        else:
            return public_quiz
    else:
        return quiz


@router.post("/start/{quiz_id}")
async def start_quiz(quiz_id: str, user: User = Depends(get_current_user)):
    try:
        quiz_id = uuid.UUID(quiz_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="badly formed quiz id")
    quiz = await Quiz.objects.get_or_none(id=quiz_id, user_id=user.id)
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


@router.put("/update/{quiz_id}")
async def update_quiz(quiz_id: str, quiz_input: QuizInput, user: User = Depends(get_current_user)):
    try:
        quiz_id = uuid.UUID(quiz_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="badly formed quiz id")
    quiz = await Quiz.objects.get_or_none(id=quiz_id, user_id=user.id)
    if quiz is None:
        return JSONResponse(status_code=404, content={"detail": "quiz not found"})
    else:
        # print(quiz_input)
        # print(quiz)
        quiz.title = quiz_input.title
        quiz.public = quiz_input.public
        quiz.description = quiz_input.description
        quiz.updated_at = datetime.now()
        quiz.questions = quiz_input.dict()["questions"]
        return await quiz.update()


@router.post("/import/{quiz_id}")
async def import_quiz_route(quiz_id: str, user: User = Depends(get_current_user)):
    try:
        return await import_quiz(quiz_id, user)
    except ValidationError:
        raise HTTPException(status_code=400, detail="THis quiz in't (yet) supported")


@router.delete("/delete/{quiz_id}")
async def delete_quiz(quiz_id: str, user: User = Depends(get_current_user)):
    try:
        quiz_id = uuid.UUID(quiz_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="badly formed quiz id")
    quiz = await Quiz.objects.get_or_none(id=quiz_id, user_id=user.id)

    if quiz is None:
        return JSONResponse(status_code=404, content={"detail": "quiz not found"})
    pics_to_delete = []
    pic_name_regex = re.compile("^.*/(.{36}--.{36})$")
    for question in quiz.questions:
        try:
            if question["image"] is not None:
                if not str(question["image"]).startswith("https://i.imgur.com/"):
                    pics_to_delete.append(pic_name_regex.match(question["image"]).group(1))
        except KeyError:
            pass
    if len(pics_to_delete) != 0:
        await storage.delete(pics_to_delete)
    return await quiz.delete()
