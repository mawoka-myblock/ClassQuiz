# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


from classquiz.db.models import User, UserSession
from fastapi import Response, Request, HTTPException
import os
import uuid
from classquiz.config import settings, redis
from datetime import timedelta, datetime
from classquiz.auth import create_access_token

settings = settings()


async def log_user_in(user: User, request: Request, response: Response):
    if user is None:
        raise HTTPException(status_code=401, detail="User not matched!")
    remote_ip = None
    if request.headers.get("X-Forwarded-For") is None:
        remote_ip = request.client.host

    else:
        if "," in request.headers.get("X-Forwarded-For"):
            remote_ip = request.headers.get("X-Forwarded-For").split(", ")[0]
        else:
            remote_ip = request.headers.get("X-Forwarded-For")
    session_key = os.urandom(32).hex()
    user_session = UserSession(
        user=user,
        session_key=session_key,
        ip_address=remote_ip,
        user_agent=request.headers.get("User-Agent"),
        id=uuid.uuid4(),
    )
    await user_session.save()
    # await user_session.save()
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    await redis.set(access_token, user.email, ex=settings.access_token_expire_minutes * 60)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 365,
    )
    response.set_cookie(
        key="rememberme_token", value=session_key, httponly=True, samesite="lax", max_age=60 * 60 * 24 * 365
    )
    return {"access_token": access_token, "token_type": "bearer"}


async def rememberme_check(rememberme_token: str, response: Response):
    user_session: UserSession | None = (
        await UserSession.objects.filter(session_key=rememberme_token).select_related(UserSession.user).get_or_none()
    )
    if (user_session is None) or (user_session.user is None):
        raise HTTPException(status_code=401, detail="No user session")
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes * 60)
    access_token = create_access_token(data={"sub": user_session.user.email}, expires_delta=access_token_expires)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 365,
    )
    response.set_cookie(key="expiry", value="", max_age=settings.access_token_expire_minutes * 60)
    response.status_code = 200
    await user_session.update(last_seen=datetime.now())
