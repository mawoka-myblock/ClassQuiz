#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

from functools import lru_cache

from redis import asyncio as redis_lib
import redis as redis_base_lib
from pydantic import BaseSettings, RedisDsn, PostgresDsn
import meilisearch as MeiliSearch
from typing import Optional

from classquiz.storage import Storage


class Settings(BaseSettings):
    """
    Settings class for the shop app.
    """

    root_address: str = "http://127.0.0.1:8000"
    redis: RedisDsn = "redis://localhost:6379/0?decode_responses=True"
    skip_email_verification: bool = False
    db_url: str | PostgresDsn = "postgresql://postgres:mysecretpassword@localhost:5432/classquiz"
    hcaptcha_key: str | None = None
    recpatcha_key: str | None = None
    mail_address: str
    mail_password: str
    mail_username: str
    mail_server: str
    mail_port: int
    secret_key: str
    access_token_expire_minutes: int = 30
    cache_expiry: int = 86400
    sentry_dsn: str | None
    meilisearch_url: str = "http://127.0.0.1:7700"
    meilisearch_index: str = "classquiz"
    google_client_id: Optional[str]
    google_client_secret: Optional[str]
    github_client_id: Optional[str]
    github_client_secret: Optional[str]
    telemetry_enabled: bool = True

    # storage_backend
    storage_backend: str | None = "deta"
    # if storage_backend == "deta":
    deta_project_key: str | None
    deta_project_id: str | None

    # if storage_backend == "local":
    storage_path: str | None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def settings() -> Settings:
    return Settings()


redis: redis_base_lib.client.Redis = redis_lib.Redis().from_url(settings().redis)
storage: Storage = Storage(
    backend=settings().storage_backend,
    deta_key=settings().deta_project_key,
    deta_id=settings().deta_project_id,
    storage_path=settings().storage_path,
)

meilisearch = MeiliSearch.Client(settings().meilisearch_url)
