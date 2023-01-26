#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

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
        quizzes = await Quiz.objects.all(user_id=user_id, public=True, imported_from_kahoot=imported)
    if len(quizzes) == 0:
        raise HTTPException(status_code=404, detail="no quizzes found")
    else:
        return quizzes
