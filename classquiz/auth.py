# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0

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

from classquiz.cache import get_cache
from classquiz.config import settings, redis
from datetime import datetime
from classquiz.db.models import User, TokenData, ApiKey

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
    user = await get_user_from_mail(email=token_data.email)
    if user is None:
        raise credentials_exception
    if user.username not in settings.mods:
        raise credentials_exception
    return user


async def get_admin_user(token: str = Depends(oauth2_scheme)) -> User:
    user = await get_current_user(token)
    admin_user = await User.objects.order_by(User.created_at.asc()).get()
    if admin_user.id == user.id:
        return user
    else:
        raise credentials_exception


async def get_current_user_optional(token: str = Depends(oauth2_scheme)) -> User | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        token_data = TokenData(email=email)
    except JWTError:
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
