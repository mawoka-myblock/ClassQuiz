# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
# SPDX-FileCopyrightText: 2026 frogQuiz contributors
#
# SPDX-License-Identifier: MPL-2.0


import json
import random
import uuid
from datetime import datetime
from random import randint

import ormar.exceptions

from frogquiz.helpers import (
    extract_image_ids_from_quiz,
    generate_spreadsheet,
    handle_import_from_excel,
    release_quiz_images,
)
from fastapi import APIRouter, Depends, HTTPException, Header, Request, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import ValidationError, BaseModel

from frogquiz.auth import get_current_user, get_current_user_optional, verify_anon_secret
from frogquiz.config import redis, settings, storage, meilisearch
from frogquiz.db.models import Quiz, User, PlayGame, GameInLobby, QuizQuestion, QuizQuestionType
from frogquiz.helpers.box_controller import generate_code
from frogquiz.helpers.completeness import unfinished_questions
from frogquiz.helpers.ratelimit import rate_limit
from frogquiz.kahoot_importer.import_quiz import import_quiz
import urllib.parse


def _quiz_expired(quiz: Quiz) -> bool:
    return quiz.expire_at is not None and quiz.expire_at < datetime.now()


async def _find_own_quiz(quiz_id: uuid.UUID, user: User | None, anon_secret: str | None) -> Quiz | None:
    """The quiz if the caller owns it, by account or by anonymous secret.

    The two are checked independently rather than as either/or. Someone who makes
    a quiz without an account and then signs in, without claiming it first, still
    holds its secret, and used to find their own quiz 404ing on start and delete.
    """
    if user is not None:
        quiz = await Quiz.objects.get_or_none(id=quiz_id, user_id=user.id)
        if quiz is not None:
            return quiz
    if anon_secret is None:
        return None
    quiz = await Quiz.objects.get_or_none(id=quiz_id, user_id=None)
    if quiz is None or _quiz_expired(quiz) or not verify_anon_secret(anon_secret, quiz.anon_secret):
        return None
    return quiz


settings = settings()

router = APIRouter()


def _captcha_configured() -> bool:
    """Whether a captcha provider is actually set up. See start_quiz."""
    if settings.hcaptcha_key is None and settings.recaptcha_key is None:
        return False
    return True


@router.get("/get/{quiz_id}")
async def get_quiz_from_id(
    quiz_id: str,
    user: User | None = Depends(get_current_user_optional),
    x_anon_secret: str | None = Header(default=None, alias="X-Anon-Secret"),
):
    try:
        quiz_id = uuid.UUID(quiz_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="badly formed quiz id")
    if user is None and x_anon_secret is None:
        # Kept as it was: signed out and without a secret, this route has only
        # ever served public quizzes, and a caller with neither got a 401.
        raise HTTPException(status_code=401, detail="Not authenticated")
    quiz = await _find_own_quiz(quiz_id, user, x_anon_secret)
    if quiz is not None:
        # The secret is a credential, not quiz content; the editor has it already.
        return quiz.model_dump(exclude={"anon_secret"})
    public_quiz = await Quiz.objects.get_or_none(id=quiz_id, public=True)
    if public_quiz is None:
        return JSONResponse(status_code=404, content={"detail": "quiz not found"})
    return public_quiz


class PublicQuizResponseUser(BaseModel):
    username: str
    id: uuid.UUID


# `anon_secret` is excluded deliberately: the response is unauthenticated, and
# although the stored value is a SHA-256 of 256 random bits and so not
# reversible, it is an ownership credential and has no business being served.
class PublicQuizResponse(Quiz.get_pydantic(exclude={"questions", "anon_secret"})):
    user_id: PublicQuizResponseUser | None
    questions: list[QuizQuestion]
    likes: int
    dislikes: int
    views: int
    plays: int


@router.get("/get/public/{quiz_id}")
async def get_public_quiz(quiz_id: uuid.UUID):
    quiz = await Quiz.objects.select_related("user_id").get_or_none(id=quiz_id)
    if quiz is None or _quiz_expired(quiz):
        return JSONResponse(status_code=404, content={"detail": "quiz not found"})
    else:
        quiz.views += 1
        await quiz.update()
        return PublicQuizResponse(**quiz.model_dump())


@router.post("/start/{quiz_id}")
async def start_quiz(
    request: Request,
    quiz_id: str,
    game_mode: str,
    # Defaulted to True, which only looked harmless because the one caller
    # (lib/dashboard/start_game.svelte) sends 'False' explicitly. Any other caller got a
    # game with a captcha nobody can solve -- the join page needs a sitekey to render a
    # widget -- and which check_captcha then passed for everyone, because with no secret
    # configured it fell through to return True. Off unless asked for.
    captcha_enabled: bool = False,
    custom_field: str | None = None,
    cqcs_enabled: bool = False,
    randomize_answers: bool = False,
    user: User | None = Depends(get_current_user_optional),
    x_anon_secret: str | None = Header(default=None, alias="X-Anon-Secret"),
):
    try:
        quiz_id = uuid.UUID(quiz_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="badly formed quiz id")
    if user is None:
        await rate_limit(request, "quiz_start_anon", limit=20, window_seconds=60)
    quiz = await _find_own_quiz(quiz_id, user, x_anon_secret)
    if quiz is None and user is not None:
        # Signed-out callers get no public-quiz fallback: hosting without an
        # account is only allowed for a quiz that was itself created anonymously
        # and whose secret the caller holds, not for hosting someone else's quiz.
        quiz = await Quiz.objects.get_or_none(id=quiz_id, public=True)
    if quiz is None or _quiz_expired(quiz):
        return JSONResponse(status_code=404, content={"detail": "quiz not found"})
    if not quiz.questions:
        # An empty quiz used to open a live game with nothing in it.
        return JSONResponse(status_code=400, content={"detail": "quiz has no questions"})
    unfinished = unfinished_questions(quiz.questions)
    if unfinished:
        # The editor autosaves, so a quiz can be saved half-written (MVP.md D14). Starting
        # one would put a question with no right answer, or no answers, on the projector.
        numbers = ", ".join(str(n) for n in unfinished)
        return JSONResponse(
            status_code=400,
            content={"detail": f"This quiz is a draft. Finish question {numbers} in the editor first."},
        )
    quiz.plays += 1
    await quiz.update()
    game_pin = randint(100000, 999999)
    if custom_field == "":
        custom_field = None
    game = await redis.get(f"game:{game_pin}")
    while game is not None:
        game_pin = randint(100000, 999999)
        game = await redis.get(f"game:{game_pin}")

    if randomize_answers:
        for question in quiz.questions:
            if question["type"] == QuizQuestionType.RANGE:
                continue
            if question["type"] == QuizQuestionType.SLIDE:
                continue
            random.shuffle(question["answers"])

    game = PlayGame(
        quiz_id=quiz_id,
        game_pin=str(game_pin),
        questions=quiz.questions,
        game_id=uuid.uuid4(),
        title=quiz.title,
        description=quiz.description,
        # A captcha with no secret cannot verify anything, so asking for one here is a
        # misconfiguration rather than a preference. Refusing to store it is what keeps
        # check_captcha's fail-closed branch unreachable: there is no way to open a game
        # that demands a captcha the server could never check.
        captcha_enabled=captcha_enabled and _captcha_configured(),
        cover_image=quiz.cover_image,
        game_mode=game_mode,
        user_id=user.id if user is not None else None,
        background_color=quiz.background_color,
        custom_field=custom_field,
        background_image=quiz.background_image,
    )
    code = None
    if cqcs_enabled:
        code = generate_code(6)
        await redis.set(f"game:cqc:code:{code}", game_pin, ex=3600)
    await redis.set(f"game:{str(game.game_pin)}", game.model_dump_json(), ex=18000)

    if user is not None:
        await redis.set(f"game_pin:{user.id}:{quiz_id}", game_pin, ex=18000)
        await redis.set(
            f"game_in_lobby:{user.id.hex}",
            GameInLobby(game_id=game.game_id, game_pin=str(game_pin), quiz_title=quiz.title).model_dump_json(),
            ex=900,
        )
    return {**quiz.model_dump(exclude={"id"}), **game.model_dump(exclude={"questions"}), "cqc_code": code}


@router.post("/claim/{quiz_id}")
async def claim_quiz(
    request: Request,
    quiz_id: uuid.UUID,
    user: User = Depends(get_current_user),
    x_anon_secret: str = Header(..., alias="X-Anon-Secret"),
):
    """Attach a quiz created without an account to the caller's account.

    Requires being signed in -- claiming isn't itself something an anonymous
    caller can do. A wrong secret and a nonexistent/already-claimed/expired
    quiz all 404 identically, so this can't be used to probe which quiz IDs
    exist or which ones are still unclaimed.
    """
    await rate_limit(request, "quiz_claim", limit=20, window_seconds=60)
    quiz = await Quiz.objects.get_or_none(id=quiz_id, user_id=None)
    if quiz is None or _quiz_expired(quiz) or not verify_anon_secret(x_anon_secret, quiz.anon_secret):
        raise HTTPException(status_code=404, detail="quiz not found")
    quiz.user_id = user.id
    quiz.anon_secret = None
    quiz.expire_at = None
    await quiz.update()
    return quiz


class CheckIfCaptchaEnabledResponse(BaseModel):
    enabled: bool
    game_mode: str | None = None
    custom_field: str | None = None


@router.get("/play/check_captcha/{game_pin}", response_model=CheckIfCaptchaEnabledResponse)
async def check_if_captcha_enabled(game_pin: str):
    game = await redis.get(f"game:{game_pin}")
    if game is None:
        return JSONResponse(status_code=404, content={"detail": "game not found"})
    game = PlayGame.model_validate_json(game)
    if game.captcha_enabled:
        return CheckIfCaptchaEnabledResponse(enabled=True, game_mode=game.game_mode, custom_field=game.custom_field)
    else:
        return CheckIfCaptchaEnabledResponse(enabled=False, game_mode=game.game_mode, custom_field=game.custom_field)


@router.get("/join/{game_pin}", deprecated=True)
async def get_game_id(game_pin: str):
    # This used to hand the game_id -- the host's credential -- to anyone who knew
    # the PIN, which is to say every player in the room; with it they could take the
    # host seat or drive the game from register_as_remote. Nothing in the frontend
    # calls it. The route stays, answering 410, so an old client gets a clear answer
    # rather than a 404 that looks like a typo'd PIN.
    raise HTTPException(status_code=410, detail="this endpoint has been retired")


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


@router.post("/import/{quiz_id}")
async def import_quiz_route(quiz_id: str, user: User = Depends(get_current_user)):
    if user.storage_used > settings.free_storage_limit:
        raise HTTPException(status_code=409, detail="Storage limit reached")
    resp_data = await import_quiz(quiz_id, user)
    try:
        if type(resp_data) is int:
            raise HTTPException(status_code=resp_data, detail="kahoot")
        else:
            return resp_data
    except ValidationError:
        raise HTTPException(400, detail="unsupported")


@router.delete("/delete/{quiz_id}")
async def delete_quiz(
    request: Request,
    quiz_id: str,
    user: User | None = Depends(get_current_user_optional),
    x_anon_secret: str | None = Header(default=None, alias="X-Anon-Secret"),
):
    """Delete a quiz, as its signed-in owner or as the anonymous creator.

    Without the anonymous path a quiz made at /create?anon=true could be edited
    and hosted by whoever holds its secret but never deleted by them, so the only
    way out of a mistake was to wait for the 30-day sweep.

    A wrong secret and a nonexistent quiz both 404, matching /claim, so this
    can't be used to probe which quiz IDs exist.
    """
    try:
        quiz_id = uuid.UUID(quiz_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="badly formed quiz id")
    if user is None:
        await rate_limit(request, "quiz_delete_anon", limit=20, window_seconds=60)
    quiz = await _find_own_quiz(quiz_id, user, x_anon_secret)

    if quiz is None:
        return JSONResponse(status_code=404, content={"detail": "quiz not found"})
    # Captured before the delete, released after: while the quiz row exists every one of
    # its images still counts as referenced, and the reference count is the whole point.
    image_ids = extract_image_ids_from_quiz(quiz)
    meilisearch.index(settings.meilisearch_index).delete_document(str(quiz.id))
    deleted = await quiz.delete()
    await release_quiz_images(image_ids)
    return deleted


@router.get("/export_data/{export_token}", response_class=StreamingResponse)
async def export_quiz_answers(export_token: str, game_pin: str):
    data = await redis.get(f"export_token:{export_token}")
    if data is None:
        raise HTTPException(status_code=404, detail="export token not found")
    data = json.loads(data)
    data2 = await redis.get(f"game:{game_pin}")
    game_data = PlayGame.model_validate_json(data2)
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
            "Content-Disposition": f"attachment;filename=frogQuiz-{urllib.parse.quote(quiz.title)}-{datetime.now().strftime('%m-%d-%Y')}.xlsx"  # noqa: E501
        },
    )


@router.post("/excel-import")
async def import_from_excel(file: UploadFile = File(), user: User = Depends(get_current_user)) -> Quiz:
    quiz = await handle_import_from_excel(file.file, user)
    return Quiz.model_validate(quiz.model_dump(exclude={"user_id": ...}))
