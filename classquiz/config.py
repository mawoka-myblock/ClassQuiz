from pydantic import BaseSettings, RedisDsn
import redis.asyncio as redis_lib


class Settings(BaseSettings):
    """
    Settings class for the shop app.
    """
    root_address: str = "http://127.0.0.1:8000"
    redis: RedisDsn = "redis://localhost:6379/0?decode_responses=True"
    skip_email_verification: bool = False
    db_url: str = "sqlite:///classquiz.db"
    hcaptcha_key: str
    mail_address: str
    mail_password: str
    mail_username: str
    mail_server: str
    mail_port: int
    secret_key: str
    access_token_expire_minutes: int = 30
    cache_expiry: int = 86400

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


settings = Settings()
redis: redis_lib.client.Redis = redis_lib.Redis().from_url(settings.redis)
