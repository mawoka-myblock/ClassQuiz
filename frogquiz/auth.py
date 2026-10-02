# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
# SPDX-FileCopyrightText: 2026 frogQuiz contributors
#
# SPDX-License-Identifier: MPL-2.0

import hashlib
import hmac
import uuid
from datetime import timedelta
from typing import Dict
from typing import Optional
from typing import Union

from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
from passlib.hash import argon2

from frogquiz.cache import get_cache
from frogquiz.config import settings, redis
from datetime import datetime
from frogquiz.db.models import User, TokenData, ApiKey

settings = settings()

pwd_context = argon2
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        try:
            authorization = request.state.access_token
        except AttributeError:
            authorization: str = request.cookies.get(
                "access_token"
            )  # changed to accept access token from httpOnly Cookie
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/api/v1/users/token/cookie")
# Same scheme, but doesn't 401 on its own when no cookie/header is present at
# all -- get_current_user_optional needs to actually reach its body and
# return None for a fully anonymous caller, not have the dependency itself
# raise first.
oauth2_scheme_optional = OAuth2PasswordBearerWithCookie(tokenUrl="/api/v1/users/token/cookie", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def get_user_from_mail(email: str) -> Union[User, None]:
    return await get_cache(criteria="email", content=email)


async def get_user_from_username(username: str) -> Union[User, None]:
    return await get_cache(criteria="username", content=username)


async def get_user_from_id(id: str) -> Union[User, None]:
    return await get_cache(criteria="id", content=id)


async def authenticate_user(email: str, password: str) -> Union[User, bool]:
    user = await get_user_from_mail(email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def hash_anon_secret(secret: str) -> str:
    """Hash the ownership secret for a quiz created without an account.

    Only this hash is ever persisted; the raw secret lives in the creator's
    browser and is returned exactly once, at creation.
    """
    return hashlib.sha256(secret.encode()).hexdigest()


def verify_anon_secret(secret: str | None, expected_hash: str | None) -> bool:
    """Constant-time check of a caller-supplied secret against a stored hash.

    Both a missing secret and a quiz with none set return False rather than
    raising, so callers can use this directly in an `if` without needing to
    special-case "no secret was ever issued".
    """
    if not secret or not expected_hash:
        return False
    return hmac.compare_digest(hash_anon_secret(secret), expected_hash)


def hash_session_key(session_key: str) -> str:
    """Hash a remember-me session key for storage.

    The key is 32 random bytes, so a fast hash is enough here -- this protects
    against a database read handing over live sessions, not against guessing.
    """
    return hashlib.sha256(session_key.encode()).hexdigest()


def _revocation_key(token: str) -> str:
    # Keyed by hash so live tokens are not themselves stored as Redis keys.
    return f"revoked_token:{hashlib.sha256(token.encode()).hexdigest()}"


async def revoke_token(token: str) -> None:
    """Deny a token for whatever remains of its lifetime.

    A denylist rather than an allowlist: tokens stay valid by default, so no
    issuing path has to remember to register them, and the entry expires with
    the token itself rather than accumulating.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM], options={"verify_exp": False})
    except JWTError:
        return
    expires_at = payload.get("exp")
    if expires_at is None:
        return
    remaining = int(expires_at - datetime.utcnow().timestamp())
    if remaining > 0:
        await redis.set(_revocation_key(token), "1", ex=remaining)


async def token_is_revoked(token: str) -> bool:
    """True once the token has been explicitly revoked, e.g. by logging out."""
    return await redis.get(_revocation_key(token)) is not None


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    if await token_is_revoked(token):
        raise credentials_exception
    user = await get_user_from_mail(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_moderator(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    if await token_is_revoked(token):
        raise credentials_exception
    user = await get_user_from_mail(email=token_data.email)
    if user is None:
        raise credentials_exception
    if user.username not in settings.mods:
        raise credentials_exception
    return user


async def get_admin_user(token: str = Depends(oauth2_scheme)) -> User:
    user = await get_current_user(token)
    # Was "the account with the oldest created_at", which meant deleting the admin
    # account quietly promoted whoever registered next -- with no record that it had
    # happened and no way to hand the role over deliberately. Migration b5e91c7a2d38
    # set the flag on whichever account that rule was pointing at, so nothing changed
    # hands when it shipped.
    if user.is_admin:
        return user
    raise credentials_exception


async def get_current_user_optional(token: str | None = Depends(oauth2_scheme_optional)) -> User | None:
    if token is None:
        return None
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        token_data = TokenData(email=email)
    except JWTError:
        return None
    if await token_is_revoked(token):
        return None
    user = await get_user_from_mail(email=token_data.email)
    if user is None:
        return None
    return user


async def check_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    if await token_is_revoked(token):
        raise credentials_exception
    return token_data.email


async def check_api_key(key: str) -> uuid.UUID | None:
    redis_res = await redis.get(f"apikey:{key}")
    if redis_res is None:
        key2 = await ApiKey.objects.get_or_none(key=key)
        if key2 is None:
            return None
        else:
            await redis.set(f"apikey:{key}", key2.user.id.hex, ex=3600)
            return key2.user.id
    else:
        return uuid.UUID(redis_res)
