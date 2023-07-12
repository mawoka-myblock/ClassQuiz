# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0
import enum
import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID

from pydantic import BaseModel

from classquiz.auth import get_current_user
from classquiz.db.models import User, Quiz, Rating

router = APIRouter()


#
@router.get("/user/{user_id}", response_model_include={"username", "created_at", "id"}, response_model=User)
async def get_user_by_user_id(user_id: UUID):
    user = await User.objects.get_or_none(id=user_id)
    # .select_related("quizs")
    # print(user)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    else:
        return user


@router.get("/quizzes/{user_id}", response_model_exclude={"questions", "user_id"}, response_model=list[Quiz])
async def get_quizzes_from_user(user_id: UUID, imported: bool | None = None):
    if imported is None:
        quizzes = await Quiz.objects.all(user_id=user_id, public=True)
    else:
        quizzes = await Quiz.objects.filter(
            (Quiz.imported_from_kahoot == False) | (Quiz.imported_from_kahoot == None)  # noqa
        ).all(user_id=user_id, public=True)
    if len(quizzes) == 0:
        raise HTTPException(status_code=404, detail="no quizzes found")
    else:
        return quizzes


class RateQuizInputType(str, enum.Enum):
    LIKE = "LIKE"
    DISLIKE = "DISLIKE"


class RateQuizInput(BaseModel):
    type: RateQuizInputType


@router.post("/rate/{quiz_id}")
async def rate_quiz(data: RateQuizInput, quiz_id: uuid.UUID, user: User = Depends(get_current_user)):
    quiz = await Quiz.objects.get_or_none(id=quiz_id, public=True)
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    rating = await Rating.objects.get_or_none(quiz=quiz, user=user)
    positive = True
    if data.type == RateQuizInputType.DISLIKE:
        positive = False
    if rating is not None and rating.positive == positive:
        raise HTTPException(status_code=409, detail="Rating already submitted")
    elif rating is not None and rating.positive != positive:
        await rating.delete()
        if rating.positive:
            quiz.likes -= 1
        else:
            quiz.dislikes -= 1
    rating = Rating(id=uuid.uuid4(), user=user, positive=positive, quiz=quiz, created_at=datetime.now())
    await rating.save()
    if positive:
        quiz.likes += 1
    else:
        quiz.dislikes += 1
    await quiz.update()
