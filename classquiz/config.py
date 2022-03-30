import redis.asyncio as redis_lib
from functools import lru_cache
from pydantic import BaseSettings, RedisDsn, PostgresDsn


class Settings(BaseSettings):
    """
    Settings class for the shop app.
    """
    root_address: str = "http://127.0.0.1:8000"
    redis: RedisDsn = "redis://localhost:6379/0?decode_responses=True"
    skip_email_verification: bool = False
    db_url: str | PostgresDsn = "sqlite:///classquiz.db"
    hcaptcha_key: str
    mail_address: str
    mail_password: str
    mail_username: str
    mail_server: str
    mail_port: int
    secret_key: str
    imgur_client_id: str = "b13fefc8bb1db87"
    access_token_expire_minutes: int = 30
    cache_expiry: int = 86400
    sentry_dsn: str | None = "https://4981de1f72f24fd7b5e21b8913b93a02@o661934.ingest.sentry.io/6254641"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


@lru_cache()
def settings() -> Settings:
    return Settings()


redis: redis_lib.client.Redis = redis_lib.Redis().from_url(settings().redis)
