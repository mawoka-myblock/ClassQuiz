import os

from email_validator import validate_email, EmailNotValidError
from fastapi import APIRouter, Response, HTTPException, Request, Depends, status
from datetime import timedelta, datetime
from fastapi.background import BackgroundTasks
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from classquiz.auth import (
    get_password_hash,
    verify_password,
    authenticate_user,
    create_access_token,
    get_current_user,
)
from classquiz.cache import clear_cache_for_account
from classquiz.config import redis, settings
import uuid
import bleach
from pydantic import BaseModel
from classquiz.db.models import User, UserSession, UpdatePassword, Token
from classquiz.emails import send_register_email, send_forgotten_password_email

settings = settings()
router = APIRouter()

route_user = User.get_pydantic(
    exclude={
        "id": ...,
        "verified": ...,
        "verify_key": ...,
        "created_at": ...,
        "usersessions": ...,
    }
)


async def _sign_out_everywhere(user: User) -> None:
    await UserSession.objects.filter(user=user).delete()
    await clear_cache_for_account(user)


@router.post(
    "/create",
    response_model=User,
    response_model_include={"id": ..., "verified": ..., "email": ...},
)
async def create_user(user: route_user, background_task: BackgroundTasks) -> User | JSONResponse:
    user = User(**user.dict(), id=uuid.uuid4())
    try:
        validate_email(user.email)
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail=str(e))
    user.verify_key = str(os.urandom(16).hex())
    res = await User.objects.filter((User.email == user.email) | (User.username == user.username)).all()

    if len(res) != 0:
        raise HTTPException(status_code=409, detail="User already exists")

    user.password = get_password_hash(user.password)
    user.username = bleach.clean(user.username, tags=[], strip=True)
    if len(user.username) == 32:
        return JSONResponse({"details": "Username mustn't be 32 characters long"}, 400)
    await user.save()
    background_task.add_task(send_register_email, email=user.email)
    await redis.delete("global_user_count")
    return user


@router.post("/token/cookie", response_model=Token)
async def login_for_cookie_access_token(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    remote_ip = None
    if request.headers.get("X-Forwarded-For") is None:
        if ", " in request.client.host:
            remote_ip = request.client.host.split(", ")[0]
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
        samesite="strict",
        max_age=settings.access_token_expire_minutes * 60,
    )
    response.set_cookie(key="expiry", value="", max_age=settings.access_token_expire_minutes * 60)
    response.set_cookie(key="rememberme", value="")
    response.set_cookie(key="rememberme_token", value=session_key, httponly=True, samesite="strict")
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/token/rememberme")
async def rememberme_token(request: Request, response: Response):
    rememberme_cookie = request.cookies.get("rememberme_token")
    if rememberme_cookie is None:
        raise HTTPException(status_code=400, detail="No rememberme cookie")
    user_session: UserSession | None = (
        await UserSession.objects.filter(session_key=rememberme_cookie).select_related(UserSession.user).get_or_none()
    )
    if (user_session is None) or (user_session.user is None):
        raise HTTPException(status_code=401, detail="No user session")
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes * 60)
    access_token = create_access_token(data={"sub": user_session.user.email}, expires_delta=access_token_expires)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        samesite="strict",
        max_age=settings.access_token_expire_minutes * 60,
    )
    response.set_cookie(key="expiry", value="", max_age=settings.access_token_expire_minutes * 60)
    response.status_code = 200
    await user_session.update(last_seen=datetime.now())
    return response


@router.get("/logout")
async def logout(request: Request, response: Response):
    remember_token = request.cookies.get("rememberme_token")
    if remember_token is not None:
        await UserSession.objects.filter(session_key=remember_token).delete()
    response.delete_cookie("access_token")
    response.delete_cookie("expiry")
    response.delete_cookie("rememberme")
    response.delete_cookie("rememberme_token")
    response.status_code = 302
    response.headers["Location"] = "/"
    return response


@router.get("/check")
async def check_token(user: User = Depends(get_current_user)):
    return {"email": user.email}


@router.get("/verify/{verify_key}")
async def verify_user(verify_key: str):
    user = await User.objects.filter(verify_key=verify_key).get_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.verified = True
    user.verify_key = None
    await user.update()
    return RedirectResponse(url="/account/login?verified=true")


@router.put("/password/update")
async def change_password(
    password_data: UpdatePassword,
    response: Response,
    user: User = Depends(get_current_user),
):
    if not verify_password(password_data.old_password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    user.password = get_password_hash(password_data.new_password)
    await user.update()
    await clear_cache_for_account(user)
    await UserSession.objects.filter(user=user).delete()
    response.delete_cookie("access_token")
    response.delete_cookie("expiry")
    response.delete_cookie("rememberme")
    response.delete_cookie("rememberme_token")
    return {"message": "Password updated successfully"}


@router.delete("/signout-everywhere")
async def signout_everywhere(response: Response, user: User = Depends(get_current_user)):
    await _sign_out_everywhere(user)
    response.delete_cookie("access_token")
    response.delete_cookie("expiry")
    response.delete_cookie("rememberme")
    response.delete_cookie("rememberme_token")
    return {"message": "Signout everywhere"}


@router.get("/me", response_model_exclude={"password", "verify_key", "usersessions"})
async def get_me(user: User = Depends(get_current_user)):
    return user.dict(exclude={"password", "verify_key", "usersessions"})


class ForgotPassword(BaseModel):
    email: str


@router.post("/forgot-password")
async def forgotten_password(forgot_password: ForgotPassword):
    user = await User.objects.filter(email=forgot_password.email, verified=True).get_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    await send_forgotten_password_email(user.email)
    return {"message": "Password reset email sent"}


class ResetPassword(BaseModel):
    password: str
    token: str


@router.post("/reset-password")
async def reset_password_with_token(reset_password: ResetPassword, response: Response):
    redis_res = await redis.get(f"reset_passwd:{reset_password.token}")
    if redis_res is None:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = await User.objects.filter(id=uuid.UUID(redis_res)).get_or_none()
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid token")
    user.password = get_password_hash(reset_password.password)
    await user.update()
    await _sign_out_everywhere(user)
    response.delete_cookie("access_token")
    response.delete_cookie("expiry")
    response.delete_cookie("rememberme")
    response.delete_cookie("rememberme_token")
    return {"message": "Password updated successfully"}


@router.get("/sessions/list", response_model=list[UserSession], response_model_exclude={"user", "session_key"})
async def list_sessions(user: User = Depends(get_current_user)):
    sessions = await UserSession.objects.filter(user=user).all()
    return [session.dict() for session in sessions]


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, user: User = Depends(get_current_user)):
    try:
        session_id = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session id")
    await UserSession.objects.filter(user=user, id=session_id).delete()
    return {"message": "Session deleted"}


@router.get("/session", response_model=UserSession, response_model_exclude={"user", "session_key"})
async def get_session(user: User = Depends(get_current_user)):
    session = await UserSession.objects.filter(user=user).first()
    return session
