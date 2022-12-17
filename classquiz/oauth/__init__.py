#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
from datetime import timedelta, datetime

from fastapi import APIRouter, Request, Response

from classquiz.auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from classquiz.db.models import UserSession
from classquiz.oauth import google, github


router = APIRouter()
router.include_router(google.router, prefix="/google")
router.include_router(github.router, prefix="/github")


async def rememberme_middleware(request: Request, call_next):
    rememberme_cookie = request.cookies.get("rememberme_token")
    bearer_token = request.cookies.get("access_token")
    if rememberme_cookie is not None and bearer_token is None:
        user_session: UserSession | None = (
            await UserSession.objects.filter(session_key=rememberme_cookie)
            .select_related(UserSession.user)
            .get_or_none()
        )
        if (user_session is None) or (user_session.user is None):
            response: Response = await call_next(request)
            return response
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        access_token = create_access_token(data={"sub": user_session.user.email}, expires_delta=access_token_expires)
        await user_session.update(last_seen=datetime.now())
        request.state.access_token = f"Bearer {access_token}"
        response: Response = await call_next(request)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            samesite="lax",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    else:
        response: Response = await call_next(request)
    return response
