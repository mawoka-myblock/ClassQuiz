from authlib.integrations.starlette_client import OAuth
from classquiz.config import settings
from functools import lru_cache

settings = settings()


@lru_cache()
def init_oauth() -> OAuth:
    oauth = OAuth()
    oauth.register(
        name="google",
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
    )

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
    return oauth
