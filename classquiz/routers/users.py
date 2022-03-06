import os

from email_validator import validate_email, EmailNotValidError
from fastapi import APIRouter, Response
from fastapi.background import BackgroundTasks
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from classquiz.auth import *
from classquiz.config import redis
from classquiz.db.models import *
from classquiz.emails import send_mail

router = APIRouter()

route_user = User.get_pydantic(
    exclude={"id": ..., "verified": ..., "verify_key": ..., "created_at": ..., "usersessions": ...})


@router.post("/create", response_model=User,
             response_model_include={"id": ..., "verified": ..., "email": ...})
async def create_user(user: route_user, background_task: BackgroundTasks) -> User | JSONResponse:
    user = User(**user.dict())
    try:
        validate_email(user.email)
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail=str(e))
    user.verify_key = str(os.urandom(16).hex())
    res = await User.objects.filter((User.email == user.email) | (User.username == user.username)).all()

    if len(res) != 0:
        raise HTTPException(status_code=409, detail="User already exists")

    user.password = get_password_hash(user.password)
    if len(user.username) == 32:
        return JSONResponse({"details": "Username mustn't be 32 characters long"}, 400)
    res = await user.save()
    background_task.add_task(send_mail, email=user.email)
    return user


@router.post("/token/cookie", response_model=Token)
async def login_for_cookie_access_token(request: Request, response: Response,
                                        form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    session_key = os.urandom(32).hex()
    user_session = UserSession(user=user, session_key=session_key, ip_address=request.client.host,
                               user_agent=request.headers.get("User-Agent"))
    await user_session.save()
    # await user_session.save()
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    await redis.set(access_token, user.email, ex=settings.access_token_expire_minutes * 60)

    response.set_cookie(key="access_token", value=f"Bearer {access_token}",
                        httponly=True, samesite='strict', max_age=settings.access_token_expire_minutes * 60)
    response.set_cookie(key="expiry", value="", max_age=settings.access_token_expire_minutes * 60)
    response.set_cookie(key="rememberme", value="")
    response.set_cookie(key="rememberme_token", value=session_key, httponly=True, samesite='strict')
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/token/rememberme")
async def rememberme_token(request: Request, response: Response):
    rememberme_cookie = request.cookies.get("rememberme_token")
    if rememberme_cookie is None:
        raise HTTPException(status_code=400, detail="No rememberme cookie")
    user_session: UserSession | None = await UserSession.objects.filter(session_key=rememberme_cookie).select_related(
        UserSession.user).get_or_none()
    if (user_session is None) or (user_session.user is None):
        raise HTTPException(status_code=401, detail="No user session")
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes * 60)
    access_token = create_access_token(
        data={"sub": user_session.user.email}, expires_delta=access_token_expires
    )
    response.set_cookie(key="access_token", value=f"Bearer {access_token}",
                        httponly=True, samesite='strict', max_age=settings.access_token_expire_minutes * 60)
    response.set_cookie(key="expiry", value="", max_age=settings.access_token_expire_minutes * 60)
    await user_session.update(last_seen=datetime.now())


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
