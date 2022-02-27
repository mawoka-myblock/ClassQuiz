import os

from fastapi import APIRouter, HTTPException, Response
from email_validator import validate_email, EmailNotValidError
from classquiz.auth import *
from fastapi.background import BackgroundTasks
from classquiz.emails import send_mail
from fastapi.responses import JSONResponse

from classquiz.db.models import *

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
        raise HTTPException(status_code=400, detail="User already exists")

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
    # user_session = UserSession(user=user, session_key=session_key)
    # print(user_session, "HALLO!!!!")
    # await user_session.save()
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    rememberme_token = create_access_token(
        data={"sub": user.email}, expires_delta=timedelta(days=360))
    response.set_cookie(key="access_token", value=f"Bearer {access_token}",
                        httponly=True, samesite='strict')
    response.set_cookie(key="expiry", value="", max_age=settings.access_token_expire_minutes * 60)
    response.set_cookie(key="rememberme", value="")
    response.set_cookie(key="rememberme_token", value=rememberme_token, httponly=True, samesite='strict')
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/token/rememberme")
async def rememberme_token(request: Request, response: Response):
    rememberme_cookie = request.cookies.get("rememberme_token")
    if rememberme_cookie is None:
        raise HTTPException(status_code=400, detail="No rememberme cookie")
    payload = jwt.decode(rememberme_cookie, settings.secret_key, algorithms=[ALGORITHM])
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": payload}, expires_delta=access_token_expires
    )
    response.set_cookie(key="access_token", value=f"Bearer {access_token}",
                        httponly=True, samesite='strict')
    response.set_cookie(key="expiry", value="", max_age=settings.access_token_expire_minutes * 60)


@router.get("/logout")
async def logout(request: Request, response: Response):
    remember_token = request.cookies.get("rememberme_token")
    if remember_token is not None:
        UserSession.objects.filter(session_key=remember_token).delete()
    response.delete_cookie("access_token")
    response.delete_cookie("expiry")
    response.delete_cookie("rememberme")
    response.delete_cookie("rememberme_token")
