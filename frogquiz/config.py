# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
# SPDX-FileCopyrightText: 2026 frogQuiz contributors
#
# SPDX-License-Identifier: MPL-2.0

import re
from functools import lru_cache

from redis import asyncio as redis_lib
import redis as redis_base_lib
from pydantic import field_validator, RedisDsn, PostgresDsn, BaseModel
import json
from typing import Annotated, Literal

from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict
import meilisearch as MeiliSearch
from arq import create_pool
from arq.connections import RedisSettings, ArqRedis
import logging

from frogquiz.storage import Storage

LOGGER = logging.getLogger(f"uvicorn.{__name__}")


class CustomOpenIDProvider(BaseModel):
    scopes: str | None = "openid email profile"
    server_metadata_url: str
    client_id: str
    client_secret: str


class Settings(BaseSettings):
    """
    Settings class for the shop app.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_nested_delimiter="__",
        env_file_encoding="utf-8",
    )
    root_address: str = "http://127.0.0.1:8000"
    redis: RedisDsn = "redis://localhost:6379/0?decode_responses=True"
    skip_email_verification: bool = False
    # Registration does a live DNS/MX lookup on the address's domain. Turn this off
    # for deployments on internal-only mail domains, or without outbound DNS.
    validate_email_deliverability: bool = True
    db_url: PostgresDsn | str = "postgresql://postgres:mysecretpassword@localhost:5432/frogquiz"
    hcaptcha_key: str | None = None
    recaptcha_key: str | None = None
    # Mail is optional so the app boots without it -- a self-hoster trying the stack
    # out shouldn't have to stand up an SMTP relay first. What it costs is that
    # nothing can be verified or recovered by email; see `mail_configured`, which
    # the endpoints that need mail check before doing anything.
    mail_address: str = ""
    mail_password: str = ""
    mail_username: str = ""
    mail_server: str = ""
    mail_port: int = 587
    # "starttls" is the usual 587 setup. Use "ssl" for implicit TLS on 465, and
    # "none" only for a relay on localhost -- it sends credentials in the clear.
    mail_security: Literal["starttls", "ssl", "none"] = "starttls"
    # What the From line reads as. The address itself still has to be one the relay
    # is willing to send for, or it will reject the message.
    mail_from_name: str = "frogQuiz"
    secret_key: str
    access_token_expire_minutes: int = 30
    # Off only for test runs, which log in far more often than a real client.
    rate_limit_enabled: bool = True
    # How many proxies sit in front of the app, counting from it outwards. 1 is the
    # bundled Caddy. Set 2 when a CDN or Netlify proxies to Caddy, or every user
    # shares one rate-limit bucket -- see client_ip() for what raising it costs.
    trusted_proxy_hops: int = 1
    cache_expiry: int = 86400
    meilisearch_url: str = "http://127.0.0.1:7700"
    meilisearch_index: str = "frogquiz"
    google_client_id: str | None = None
    google_client_secret: str | None = None
    github_client_id: str | None = None
    github_client_secret: str | None = None
    custom_openid_provider: CustomOpenIDProvider | None = None
    telemetry_enabled: bool = True
    # Per-file upload ceilings, in bytes, and the per-account total.
    #
    # Upstream had none of this: the upload route passed size=0 into storage and the
    # only cap in the product was Uppy's, in the browser, so POST /api/v1/storage/
    # took a file of any size from an unauthenticated caller. See upload_limits().
    #
    # 8MB is roughly a 4000x3000 JPEG at quality 85 -- more than a question image
    # ever needs on a projector, and the editor compresses before it uploads anyway.
    # Kahoot allows 50MB per question image and 5MB per cover; we are an internal
    # tool on free-tier storage, so a tighter number is the right trade.
    max_image_upload_size: int = 8_000_000
    # Only reachable with enable_video_upload on. 25MB is about 30 seconds of 1080p.
    max_video_upload_size: int = 25_000_000
    # Video upload is off: /edit/videos is hidden for the MVP and the editor passes
    # video_upload={false}, so leaving video/mp4 accepted only left an unbounded
    # upload path with no UI in front of it. Flip this and unhide the route together.
    enable_video_upload: bool = False
    # 256MiB per account, down from upstream's ~1.07GB. Thirty quizzes with a cover
    # and a question image each is a few MB; the old number was sized for a public
    # SaaS with paid tiers behind it, not a team on a free database.
    free_storage_limit: int = 268_435_456
    pixabay_api_key: str | None = None
    mods: list[str] = []
    registration_disabled: bool = False

    @property
    def mail_configured(self) -> bool:
        """Whether there is enough here to reach a mail server at all."""
        return bool(self.mail_server and self.mail_address)
    # Physical-buzzer hardware and the QuizTivity page builder are not used by the
    # team. Their entry points were taken out of the UI in PR #5, but the API
    # routers stayed registered and callable. Off by default; flip to re-enable.
    enable_box_controller: bool = False
    enable_quiztivity: bool = False
    # TOTP and its backup codes are cut from the MVP: the team signs in with a password,
    # and company SSO is the route to a second factor rather than an authenticator app.
    # Turning this back on restores both the setup endpoints and the login step.
    enable_totp: bool = False
    # WebAuthn security keys and quiz ratings have no UI in the MVP (MVP.md D11). Like
    # TOTP, only the endpoints that create something are gated: a key registered before
    # the cut can still be listed, deleted and used to sign in.
    enable_webauthn: bool = False
    enable_ratings: bool = False
    # /api/v1/internal/testing returns a full user row, password hash included, and
    # takes SECRET_KEY in the query string. It exists for the test suite; never set
    # this in production.
    enable_testing_routes: bool = False
    # The IP lookup has no caller, and its provider (ip-api.com) only serves HTTP free.
    enable_ip_lookup: bool = False
    # Origins allowed to call the API / socket.io cross-site (e.g. a Netlify-hosted frontend).
    # Empty means same-origin only, which is what the bundled Caddy setup uses.
    # Accepts a JSON list or a plain comma-separated string.
    # NoDecode keeps pydantic-settings from JSON-parsing this first, which is what
    # made the documented comma-separated form raise before the validator below ran.
    cors_origins: Annotated[list[str], NoDecode] = []

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors_origins(cls, v):
        # NoDecode means this sees the raw environment string, so both documented
        # forms are parsed here: a JSON list, or a plain comma-separated list.
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            if v.startswith("["):
                v = json.loads(v)
            else:
                return [origin.strip().rstrip("/") for origin in v.split(",") if origin.strip()]
        if isinstance(v, list):
            return [str(origin).strip().rstrip("/") for origin in v if str(origin).strip()]
        return v

    # storage_backend
    storage_backend: str  # either "local" or "s3"

    # if storage_backend == "local":
    storage_path: str | None = None

    # if storage_backend == "s3":
    s3_access_key: str | None = None
    s3_secret_key: str | None = None
    s3_bucket_name: str = "frogquiz"
    s3_base_url: str | None = None


async def initialize_arq():
    # skipcq: PYL-W0603
    global arq
    arq = await create_pool(RedisSettings.from_dsn(settings.redis))


@lru_cache()
def settings() -> Settings:
    return Settings()


pool = redis_lib.ConnectionPool().from_url(str(settings().redis))

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

def upload_limits() -> dict[str, int]:
    """Accepted upload types, mapped to the largest file allowed for each.

    One table, so "is this type allowed" and "how big may it be" cannot disagree --
    and so the editor's file picker can be told the same numbers rather than carrying
    its own copy (GET /api/v1/storage/limits).

    SVG is deliberately absent: it is a script-injection vector, and nothing in a quiz
    needs one.
    """
    s = settings()
    limits = {
        "image/png": s.max_image_upload_size,
        "image/jpeg": s.max_image_upload_size,
        "image/gif": s.max_image_upload_size,
        "image/webp": s.max_image_upload_size,
    }
    if s.enable_video_upload:
        limits["video/mp4"] = s.max_video_upload_size
    return limits


UPLOAD_LIMITS = upload_limits()

# Kept as a name because it reads better at the call site and in the tests. It is the
# key set of UPLOAD_LIMITS, never a second list to keep in step.
ALLOWED_MIME_TYPES = list(UPLOAD_LIMITS)

# The largest upload any type allows. Used for the cheap Content-Length rejection in
# the request-size middleware, which runs before the body is read and so cannot know
# the content type yet.
MAX_UPLOAD_SIZE = max(UPLOAD_LIMITS.values())

server_regex = rf"^{re.escape(settings().root_address)}/api/v1/storage/download/.{{36}}--.{{36}}$"
