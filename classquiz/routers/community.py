# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


from fastapi import APIRouter, HTTPException
from uuid import UUID

from classquiz.db.models import User, Quiz

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
