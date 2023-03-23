#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import re
from functools import lru_cache

from redis import asyncio as redis_lib
import redis as redis_base_lib
from pydantic import BaseSettings, RedisDsn, PostgresDsn, BaseModel
import meilisearch as MeiliSearch
from typing import Optional
import stripe as stripe_lib

from classquiz.storage import Storage


class CustomOpenIDProvider(BaseModel):
    scopes: str = "openid email profile"
    server_metadata_url: str
    client_id: str
    client_secret: str


class StripeConfig(BaseModel):
    api_key: str
    annual_id: str
    monthly_id: str
    webhook_secret: str


class Settings(BaseSettings):
    """
    Settings class for the shop app.
    """

    root_address: str = "http://127.0.0.1:8000"
    redis: RedisDsn = "redis://localhost:6379/0?decode_responses=True"
    skip_email_verification: bool = False
    db_url: str | PostgresDsn = "postgresql://postgres:mysecretpassword@localhost:5432/classquiz"
    hcaptcha_key: str | None = None
    recaptcha_key: str | None = None
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
    custom_openid_provider: CustomOpenIDProvider | None = None
    telemetry_enabled: bool = True
    stripe: StripeConfig | None

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
        env_nested_delimiter = "__"


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

ALLOWED_TAGS_FOR_QUIZ = ["b", "strong", "i", "em", "small", "mark", "del", "sub", "sup"]

server_regex = rf"^{re.escape(settings().root_address)}/api/v1/storage/download/.{{36}}--.{{36}}$"

stripe = None
stripe_enabled = False
if settings().stripe is not None:
    stripe_enabled = True
    stripe = stripe_lib
    stripe.api_key = settings().stripe.api_key
