# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0
import uuid

from fastapi import APIRouter, Depends, Response, HTTPException
from pydantic import BaseModel

from classquiz.auth import get_current_moderator
from classquiz.db.models import User, Quiz

router = APIRouter()


@router.get("/status")
async def get_mod_status(resp: Response, user: User = Depends(get_current_moderator)):
    resp.status_code = 200
    resp.set_cookie("moderator", "yes", path="/")
    resp.headers.update({"Content-Type": "application/json"})
    resp.body = '{"status": "ok"}'
    return resp


@router.get("/quizzes")
async def get_newest_quizzes(
    page: int = 1, all: bool = False, user: User = Depends(get_current_moderator)  # skipcq: PYL-W0622
) -> list[Quiz]:
    if page < 1:
        raise HTTPException(status_code=400, detail="page 1 is the first")
    if all:
        quizzes = (
            await Quiz.objects.paginate(page=page)
            .order_by(Quiz.updated_at.desc())
            .filter(Quiz.public == True)  # noqa: E712
            .all()
        )
    else:
        # noinspection PyComparisonWithNone
        quizzes = (
            await Quiz.objects.paginate(page=page)
            .order_by(Quiz.updated_at.desc())
            .filter(Quiz.public == True)  # noqa: E712
            .filter(Quiz.mod_rating == None)  # noqa: E711
            .all()
        )
    return quizzes


class SetModRatingForQuizInput(BaseModel):
    rating: int | None = None


@router.post("/rating/set/{quiz_id}")
async def set_mod_rating_for_quiz(
    data: SetModRatingForQuizInput, quiz_id: uuid.UUID, user: User = Depends(get_current_moderator)
) -> Quiz:
    quiz = await Quiz.objects.get_or_none(public=True, id=quiz_id)
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    quiz.mod_rating = data.rating
    return await quiz.update()
