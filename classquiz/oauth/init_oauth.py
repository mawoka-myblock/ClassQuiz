# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


from authlib.integrations.starlette_client import OAuth
from classquiz.config import settings, redis
from functools import lru_cache
import json

settings = settings()


class RedisCache:
    def __init__(self) -> None:
        pass

    async def get(self, key: str) -> str | None:
        value = await redis.get(f"authlib:{key}")
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    async def set(self, key: str, value: str, expires: int | None = None):
        data = json.dumps(value)
        await redis.set(f"authlib:{key}", data, ex=expires)

    async def delete(self, key: str) -> None:
        await redis.delete(f"authlib:{key}")


@lru_cache()
def init_oauth() -> OAuth:
    oauth = OAuth(cache=RedisCache())
    if settings.google_client_secret is not None and settings.google_client_id is not None:
        oauth.register(
            name="google",
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
        )
    if settings.github_client_id is not None and settings.github_client_secret is not None:
        oauth.register(
            name="github",
            client_kwargs={"scope": "read:user user:email"},
            access_token_url="https://github.com/login/oauth/access_token",
            access_token_params=None,
            authorize_url="https://github.com/login/oauth/authorize",
            authorize_params=None,
            api_base_url="https://api.github.com/",
            client_id=settings.github_client_id,
            client_secret=settings.github_client_secret,
        )
    if (
        settings.custom_openid_provider is not None
        and settings.custom_openid_provider.client_id is not None
        and settings.custom_openid_provider.client_secret is not None
    ):
        oauth.register(
            name="custom",
            client_kwargs={"scope": settings.custom_openid_provider.scopes},
            server_metadata_url=settings.custom_openid_provider.server_metadata_url,
            client_id=settings.custom_openid_provider.client_id,
            client_secret=settings.custom_openid_provider.client_secret,
        )
    return oauth
