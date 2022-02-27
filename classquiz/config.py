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
    mail_address: str
    mail_password: str
    mail_username: str
    mail_server: str
    mail_port: int
    secret_key: str
    minio_url: str = "127.0.0.1"
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str
    minio_secure: bool = True
    access_token_expire_minutes: int = 30
    cache_expiry: int = 86400
    typesense_api_key: str
    typesense_host: str = "localhost"
    typesense_port: int = 8108
    typesense_protocol: str = "http"
    typesense_timeout: int = 2

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


settings = Settings()
redis: redis_lib.client.Redis = redis_lib.Redis().from_url(settings.redis)
