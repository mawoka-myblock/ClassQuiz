#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json
import re
import uuid
from datetime import datetime
from random import randint

import ormar.exceptions

from classquiz.helpers import get_meili_data, generate_spreadsheet
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import ValidationError, BaseModel
import bleach

from classquiz.auth import get_current_user
from classquiz.config import redis, settings, storage, meilisearch
from classquiz.db.models import Quiz, QuizInput, User, PlayGame, GameInLobby, QuizQuestion
from classquiz.helpers.box_controller import generate_code
from classquiz.kahoot_importer.import_quiz import import_quiz
import html
import urllib.parse

settings = settings()

router = APIRouter()


@router.post("/create", deprecated=True)
async def create_quiz_lol(quiz_input: QuizInput, user: User = Depends(get_current_user)):
    imgur_regex = r"^https://i\.imgur\.com\/.{7}.(jpg|png|gif)$"
    server_regex = rf"^{re.escape(settings.root_address)}/api/v1/storage/download/.{36}--.{36}$"
    quiz_input.title = html.unescape(bleach.clean(quiz_input.title, tags=[], strip=True))
    quiz_input.description = html.unescape(bleach.clean(quiz_input.description, tags=[], strip=True))
    for question in quiz_input.questions:
        if question.image == "":
            question.image = None
        if (
            question.image is not None
            and not re.match(imgur_regex, question.image)
            and not re.match(server_regex, question.image)
        ):
            raise HTTPException(status_code=400, detail="image url is not valid")
    if quiz_input.cover_image == "":
        quiz_input.cover_image = None

    if quiz_input.cover_image is not None and not bool(re.match(server_regex, quiz_input.cover_image)):
        raise HTTPException(status_code=400, detail="image url is not valid")
    quiz = Quiz(**quiz_input.dict(), user_id=user.id, id=uuid.uuid4())
    await redis.delete("global_quiz_count")
    if quiz_input.public:
        meilisearch.index(settings.meilisearch_index).add_documents([await get_meili_data(quiz)])
    return await quiz.save()


@router.get("/get/{quiz_id}")
async def get_quiz_from_id(quiz_id: str, user: User | None = Depends(get_current_user)):
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


class PublicQuizResponseUser(BaseModel):
    username: str
    id: uuid.UUID


class PublicQuizResponse(Quiz.get_pydantic()):
    user_id: PublicQuizResponseUser
    questions: list[QuizQuestion]


@router.get("/get/public/{quiz_id}")
async def get_public_quiz(quiz_id: str):
    try:
        quiz_id = uuid.UUID(quiz_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="badly formed quiz id")
    quiz = await Quiz.objects.select_related("user_id").get_or_none(id=quiz_id)
    if quiz is None:
        return JSONResponse(status_code=404, content={"detail": "quiz not found"})
    else:
        return PublicQuizResponse(**quiz.dict())


@router.post("/start/{quiz_id}")
async def start_quiz(
    quiz_id: str,
    game_mode: str,
    captcha_enabled: bool = True,
    custom_field: str | None = None,
    cqcs_enabled: bool = False,
    user: User = Depends(get_current_user),
):
    try:
        quiz_id = uuid.UUID(quiz_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="badly formed quiz id")
    quiz = await Quiz.objects.get_or_none(id=quiz_id, user_id=user.id)
    if quiz is None:
        quiz = await Quiz.objects.get_or_none(id=quiz_id, public=True)
        if quiz is None:
            return JSONResponse(status_code=404, content={"detail": "quiz not found"})
    game_pin = randint(100000, 999999)
    if custom_field == "":
        custom_field = None
    game = await redis.get(f"game:{game_pin}")
    while game is not None:
        game_pin = randint(100000, 999999)
        game = await redis.get(f"game:{game_pin}")

    game = PlayGame(
        quiz_id=quiz_id,
        game_pin=str(game_pin),
        questions=quiz.questions,
        game_id=uuid.uuid4(),
        title=quiz.title,
        description=quiz.description,
        captcha_enabled=captcha_enabled,
        cover_image=quiz.cover_image,
        game_mode=game_mode,
        user_id=user.id,
        background_color=quiz.background_color,
        custom_field=custom_field,
        background_image=quiz.background_image,
    )
    code = None
    if cqcs_enabled:
        code = generate_code(6)
        await redis.set(f"game:cqc:code:{code}", game_pin, ex=3600)
    await redis.set(f"game:{str(game.game_pin)}", game.json(), ex=18000)
    await redis.set(f"game_pin:{user.id}:{quiz_id}", game_pin, ex=18000)

    await redis.set(
        f"game_in_lobby:{user.id.hex}",
        GameInLobby(game_id=game.game_id, game_pin=str(game_pin), quiz_title=quiz.title).json(),
        ex=900,
    )
    return {**quiz.dict(exclude={"id"}), **game.dict(exclude={"questions"}), "cqc_code": code}


class CheckIfCaptchaEnabledResponse(BaseModel):
    enabled: bool
    game_mode: str | None
    custom_field: str | None


@router.get("/play/check_captcha/{game_pin}", response_model=CheckIfCaptchaEnabledResponse)
async def check_if_captcha_enabled(game_pin: str):
    game = await redis.get(f"game:{game_pin}")
    if game is None:
        return JSONResponse(status_code=404, content={"detail": "game not found"})
    game = PlayGame.parse_raw(game)
    if game.captcha_enabled:
        return CheckIfCaptchaEnabledResponse(enabled=True, game_mode=game.game_mode, custom_field=game.custom_field)
    else:
        return CheckIfCaptchaEnabledResponse(enabled=False, game_mode=game.game_mode, custom_field=game.custom_field)


@router.get("/join/{game_pin}", deprecated=True)
async def get_game_id(game_pin: str):
    redis_res = await redis.get(f"game:{game_pin}")
    if redis_res is None:
        raise HTTPException(status_code=404, detail="game not found")
    else:
        return json.loads(redis_res)["game_id"]


@router.get("/list")
async def get_quiz_list(user: User = Depends(get_current_user), page_size: int | None = 10, page: int | None = 1):
    try:
        return (
            await Quiz.objects.order_by(Quiz.updated_at.desc())
            .filter(user_id=user.id)
            .paginate(page, page_size=page_size)
            .all()
        )
    except ormar.exceptions.QueryDefinitionError:
        raise HTTPException(status_code=400, detail="Invalid page(size). page(size) have to be greater than 0.")


@router.put("/update/{quiz_id}", deprecated=True)
async def update_quiz(quiz_id: str, quiz_input: QuizInput, user: User = Depends(get_current_user)):
    imgur_regex = r"^https://i\.imgur\.com\/.{7}.(jpg|png|gif)$"
    server_regex = rf"^{re.escape(settings.root_address)}/api/v1/storage/download/.{{36}}--.{{36}}$"
    for question in quiz_input.questions:
        if question.image == "":
            question.image = None
        if (
            question.image is not None
            and not bool(re.match(server_regex, question.image))
            and not bool(re.match(imgur_regex, question.image))
        ):
            raise HTTPException(status_code=400, detail="image url is not valid")
    try:
        quiz_id = uuid.UUID(quiz_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="badly formed quiz id")
    # Check Cover-Image

    if quiz_input.cover_image == "":
        quiz_input.cover_image = None

    if quiz_input.cover_image is not None and not bool(re.match(server_regex, quiz_input.cover_image)):
        raise HTTPException(status_code=400, detail="image url is not valid")

    quiz = await Quiz.objects.get_or_none(id=quiz_id, user_id=user.id)
    if quiz is None:
        return JSONResponse(status_code=404, content={"detail": "quiz not found"})
    else:
        quiz_input.description = html.unescape(bleach.clean(quiz_input.description, tags=[], strip=True))
        quiz_input.title = html.unescape(bleach.clean(quiz_input.title, tags=[], strip=True))
        meilisearch.index(settings.meilisearch_index).update_documents([await get_meili_data(quiz)])
        if quiz.public and not quiz_input.public:
            meilisearch.index(settings.meilisearch_index).delete_document(str(quiz.id))
        if not quiz.public and quiz_input.public:
            meilisearch.index(settings.meilisearch_index).add_documents([await get_meili_data(quiz)])
        quiz.title = quiz_input.title
        quiz.cover_image = quiz_input.cover_image
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
        raise HTTPException(status_code=400, detail="This quiz isn't (yet) supported")


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
            if question["image"] is not None and not str(question["image"]).startswith("https://i.imgur.com/"):
                pics_to_delete.append(pic_name_regex.match(question["image"]).group(1))
        except KeyError:
            pass
    if len(pics_to_delete) != 0:
        await storage.delete(pics_to_delete)
    meilisearch.index(settings.meilisearch_index).delete_document(str(quiz.id))
    return await quiz.delete()


@router.get("/export_data/{export_token}", response_class=StreamingResponse)
async def export_quiz_answers(export_token: str, game_pin: str):
    data = await redis.get(f"export_token:{export_token}")
    if data is None:
        raise HTTPException(status_code=404, detail="export token not found")
    data = json.loads(data)
    data2 = await redis.get(f"game:{game_pin}")
    game_data = PlayGame.parse_raw(data2)
    quiz = await Quiz.objects.get_or_none(id=game_data.quiz_id)
    if quiz is None:
        raise HTTPException(status_code=404, detail="quiz not found")

    player_fields = await redis.hgetall(f"game:{game_pin}:players:custom_fields")
    score_data = await redis.hgetall(f"game_session:{game_pin}:player_scores")
    spreadsheet = await generate_spreadsheet(
        quiz=quiz, quiz_results=data, player_fields=player_fields, player_scores=score_data
    )

    def iter_file():
        yield from spreadsheet

    await redis.delete(f"export_token:{export_token}")
    return StreamingResponse(
        iter_file(),
        media_type="application/vnd.ms-excel",
        headers={
            "Content-Disposition": f"attachment;filename=ClassQuiz-{urllib.parse.quote(quiz.title)}-{datetime.now().strftime('%m-%d-%Y')}.xlsx"  # noqa: E501
        },
    )
