#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import uuid

import asyncpg
from fastapi import APIRouter, Request, HTTPException, Response
from classquiz.config import settings

from classquiz.db.models import User, UserAuthTypes
from classquiz.auth import check_token
from classquiz.helpers.avatar import gzipped_user_avatar
from classquiz.oauth.authenticate_user import log_user_in, rememberme_check
from classquiz.oauth.init_oauth import init_oauth
from pydantic import BaseModel, ValidationError

settings = settings()

router = APIRouter()


class Userinfo(BaseModel):
    exp: int
    iat: int
    iss: str
    aud: str
    sub: uuid.UUID
    nonce: str
    email: str
    email_verified: bool


class OpenIDResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str
    scope: str
    refresh_token: str
    id_token: str
    expires_at: int
    userinfo: Userinfo


@router.get("/login")
async def openid_login(req: Request):
    if settings.google_client_secret is None or settings.google_client_id is None:
        raise HTTPException(status_code=501, detail="Custom-OAuth-Login isn't available on this server")
    oauth = init_oauth()

    return await oauth.custom.authorize_redirect(req, f"{settings.root_address}/api/v1/users/oauth/custom/auth")


@router.get("/auth")
async def auth(request: Request, response: Response):
    if settings.custom_openid_provider.client_id is None or settings.custom_openid_provider.client_secret is None:
        raise HTTPException(status_code=501, detail="Google-Login isn't available on this server")
    access_token = request.cookies.get("access_token")
    rememberme_token = request.cookies.get("rememberme_token")
    if access_token is not None:
        try:
            data = await check_token(access_token)
            if data is not None:
                return
        except HTTPException:
            pass
    if rememberme_token is not None:
        return await rememberme_check(rememberme_token=rememberme_token, response=response)
    oauth = init_oauth()

    user_data = await oauth.custom.authorize_access_token(request)
    try:
        user_data = OpenIDResponse(**user_data).userinfo
    except (TypeError, ValidationError):
        raise HTTPException(status_code=401, detail="Something went wrong.")
    print(user_data)
    user_in_db = await User.objects.get_or_none(email=user_data.email)
    if user_in_db is None:
        # REGISTER USER
        try:
            await User.objects.create(
                id=uuid.uuid4(),
                email=user_data.email,
                username=user_data.name,
                verified=user_data.email_verified,
                auth_type=UserAuthTypes.CUSTOM,
                google_uid=user_data.sub,
                avatar=gzipped_user_avatar(),
            )
        except Exception as e:
            if type(e) == asyncpg.exceptions.UniqueViolationError:
                error = True
                counter = 1
                while error:
                    try:
                        await User.objects.create(
                            id=uuid.uuid4(),
                            email=user_data.email,
                            username=f"{user_data.name}{counter}",
                            verified=user_data.email_verified,
                            auth_type=UserAuthTypes.GOOGLE,
                            google_uid=user_data.sub,
                            avatar=gzipped_user_avatar(),
                        )
                        error = False
                    except asyncpg.exceptions.UniqueViolationError:
                        counter += 1
                        error = True
            else:
                raise HTTPException(status_code=500, detail=str(e))
    user = await User.objects.get_or_none(
        email=user_data.email, google_uid=user_data.sub, auth_type=UserAuthTypes.GOOGLE, verified=True
    )

    await log_user_in(user=user, request=request, response=response)
    response.headers.append("Location", "/account/login")
    response.status_code = 302
    return response
