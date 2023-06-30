# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


from fastapi import APIRouter

from classquiz.config import redis
from pydantic import BaseModel
from classquiz.db.models import Quiz, User

router = APIRouter()


@router.get("/quizzes")
async def get_quiz_count() -> int:
    redis_res = await redis.get("global_quiz_count")
    if redis_res is None:
        quiz_res = await Quiz.objects.count()
        await redis.set("global_quiz_count", quiz_res, ex=3600)
        return quiz_res
    else:
        return int(redis_res)


@router.get("/users")
async def get_user_count() -> int:
    redis_res = await redis.get("global_user_count")
    if redis_res is None:
        quiz_res = await User.objects.filter(verified=True).count()
        await redis.set("global_user_count", quiz_res, ex=3600)
        return quiz_res
    else:
        return int(redis_res)


class CombinedOutput(BaseModel):
    quiz_count: int
    user_count: int


@router.get("/combined")
async def get_combined_count() -> CombinedOutput:
    user_count = None
    quiz_count = None
    redis_res = await redis.get("global_user_count")
    if redis_res is None:
        quiz_res = await User.objects.filter(verified=True).count()
        await redis.set("global_user_count", quiz_res, ex=3600)
        user_count = quiz_res
    else:
        user_count = int(redis_res)

    redis_res = await redis.get("global_quiz_count")
    if redis_res is None:
        quiz_res = await Quiz.objects.count()
        await redis.set("global_quiz_count", quiz_res, ex=3600)
        quiz_count = quiz_res
    else:
        quiz_count = int(redis_res)

    return CombinedOutput(quiz_count=quiz_count, user_count=user_count)
