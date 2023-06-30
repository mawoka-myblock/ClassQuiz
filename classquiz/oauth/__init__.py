# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


from datetime import timedelta, datetime

from fastapi import APIRouter, Request, Response
from fastapi.security.utils import get_authorization_scheme_param
from jose import jws, jwt, JWTError, JWSError

from classquiz.auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from classquiz.db.models import UserSession
from classquiz.oauth import google, github, custom
from classquiz.config import settings

settings = settings()

router = APIRouter()
router.include_router(google.router, prefix="/google")
router.include_router(github.router, prefix="/github")
router.include_router(custom.router, prefix="/custom")


async def rememberme_middleware(request: Request, call_next):
    rememberme_cookie = request.cookies.get("rememberme_token")
    bearer_token = request.cookies.get("access_token")
    conditions_to_handle_met = True

    scheme, param = get_authorization_scheme_param(bearer_token)

    # if bearer token is none, we can just do the request, since you can't be signed in
    if scheme is None or param is None:
        conditions_to_handle_met = False
    # if rememberme token is none, we can just do the request, since you can't be signed in
    if rememberme_cookie is None:
        conditions_to_handle_met = False

    if scheme.lower() != "bearer":
        conditions_to_handle_met = False

    # Verifying the bearer
    try:
        jwt.decode(
            param, settings.secret_key, algorithms=["HS256"]
        )  # checking if the token is valid, throws error if not
        conditions_to_handle_met = False
    except JWTError:
        try:
            jws.verify(
                param, settings.secret_key, algorithms=["HS256"]
            )  # Verifying only the signature of the jwt, throws error if signature is invalid
        except JWSError:
            conditions_to_handle_met = False

    if conditions_to_handle_met:
        user_session: UserSession | None = (
            await UserSession.objects.filter(session_key=rememberme_cookie)
            .select_related(UserSession.user)
            .get_or_none()
        )
        if (user_session is None) or (user_session.user is None):
            response: Response = await call_next(request)
            return response
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user_session.user.email}, expires_delta=access_token_expires)
        await user_session.update(last_seen=datetime.now())
        request.state.access_token = f"Bearer {access_token}"
        request.cookies.pop("access_token")
        response: Response = await call_next(request)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            samesite="lax",
            max_age=60 * 60 * 24 * 365,
        )
    else:
        response: Response = await call_next(request)
    return response
