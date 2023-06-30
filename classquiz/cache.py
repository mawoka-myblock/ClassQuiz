# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0

import uuid
from json import loads
from typing import Union

import ormar

from classquiz.config import redis, settings
from classquiz.db.models import User

settings = settings()


async def cache_account(criteria: str, content: str) -> Union[User, None]:
    async def insert_into_redis(usermodel: User, key: str):
        await redis.set(key, usermodel.json(), ex=settings.cache_expiry)

    if criteria == "email":
        try:
            res = await User.objects.get(email=content, verified=True)
        except ormar.exceptions.NoMatch:
            return None
        await insert_into_redis(res, content)
        return res
    elif criteria == "username":
        try:
            res = await User.objects.get(username=content, verified=True)
        except ormar.exceptions.NoMatch:
            return None
        await insert_into_redis(res, content)
        return res
    elif criteria == "id":
        try:
            res = await User.objects.get(id=uuid.UUID(content), verified=True)
        except ormar.exceptions.NoMatch:
            return None
        await insert_into_redis(res, content)
        return res
    else:
        return None


async def clear_cache_for_account(user: User):
    await redis.delete(user.email)
    await redis.delete(user.username)
    await redis.delete(str(user.id))


async def get_from_redis(key: str) -> Union[None, User]:
    user = await redis.get(key)
    if user is None:
        return None
    else:
        return User.parse_obj(loads(user))


async def get_cache(criteria: str, content: str) -> User:
    cache = await get_from_redis(content)
    if cache is not None:
        return cache
    else:
        return await cache_account(criteria, content)
