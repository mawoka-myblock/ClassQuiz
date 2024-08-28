# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0

import re
import os
from functools import lru_cache

from redis import asyncio as redis_lib
import redis as redis_base_lib
from pydantic import BaseSettings, RedisDsn, PostgresDsn, BaseModel
import meilisearch as MeiliSearch
from typing import Optional
from arq import create_pool
from arq.connections import RedisSettings, ArqRedis

from classquiz.storage import Storage


class CustomOpenIDProvider(BaseModel):
    scopes: str = "openid email profile"
    server_metadata_url: str
    client_id: str
    client_secret: str


class Settings(BaseSettings):
    """
    Settings class for the shop app.
    """

    root_address: str = os.getenv("ROOT_ADDRESS", "http://127.0.0.1:8000")
    redis: RedisDsn = os.getenv("REDIS_URL", "redis://localhost:6379/0?decode_responses=True")
    skip_email_verification: bool = os.getenv("SKIP_EMAIL_VERIFICATION", "False") == 'True'
    db_url: str | PostgresDsn = os.getenv("DB_URL", "postgresql://postgres:mysecretpassword@localhost:5432/classquiz")
    hcaptcha_key: str | None = None
    recaptcha_key: str | None = None
    mail_address: str = os.getenv("MAIL_ADDRESS", None)
    mail_password: str = os.getenv("MAIL_PASSWORD", None)
    mail_username: str = os.getenv("MAIL_USERNAME", None)
    mail_server: str = os.getenv("MAIL_SERVER", None)
    mail_port: int = os.getenv("MAIL_PORT", None)
    secret_key: str = os.getenv("SECRET_KEY", None)
    access_token_expire_minutes: int = 30
    cache_expiry: int = 86400
    sentry_dsn: str | None
    meilisearch_url: str = os.getenv("MEILISEARCH_URL", "http://127.0.0.1:7700")
    meilisearch_index: str = "classquiz"
    google_client_id: Optional[str]
    google_client_secret: Optional[str]
    github_client_id: Optional[str]
    github_client_secret: Optional[str]
    custom_openid_provider: CustomOpenIDProvider | None = None
    telemetry_enabled: bool = True
    free_storage_limit: int = 1074000000
    pixabay_api_key: str | None = None
    mods: list[str] = []
    registration_disabled: bool = False

    # storage_backend
    storage_backend: str = os.getenv("STORAGE_BACKEND", "local")

    # if storage_backend == "local":
    storage_path: str = os.getenv("STORAGE_PATH", None)

    # if storage_backend == "s3":
    s3_access_key: str | None
    s3_secret_key: str | None
    s3_bucket_name: str = "classquiz"
    s3_base_url: str | None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"


async def initialize_arq():
    # skipcq: PYL-W0603
    global arq
    arq = await create_pool(RedisSettings.from_dsn(settings.redis))


@lru_cache()
def settings() -> Settings:
    return Settings()


pool = redis_lib.ConnectionPool().from_url(settings().redis)

redis: redis_base_lib.client.Redis = redis_lib.Redis(connection_pool=pool)
arq: ArqRedis = ArqRedis(pool_or_conn=pool)
storage: Storage = Storage(
    backend=settings().storage_backend,
    storage_path=settings().storage_path,
    access_key=settings().s3_access_key,
    secret_key=settings().s3_secret_key,
    bucket_name=settings().s3_bucket_name,
    base_url=settings().s3_base_url,
)

meilisearch = MeiliSearch.Client(settings().meilisearch_url)

ALLOWED_TAGS_FOR_QUIZ = ["b", "strong", "i", "em", "small", "mark", "del", "sub", "sup"]

ALLOWED_MIME_TYPES = ["image/png", "video/mp4", "image/jpeg", "image/gif", "image/webp"]

server_regex = rf"^{re.escape(settings().root_address)}/api/v1/storage/download/.{{36}}--.{{36}}$"
