# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import base64
import enum
import os
import urllib.parse
import uuid

import pyotp
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, ValidationError

from classquiz.auth import verify_password
from classquiz.config import redis, settings

from classquiz.db.models import User, FidoCredentials
from webauthn import (
    generate_authentication_options,
    options_to_json,
    verify_authentication_response,
    base64url_to_bytes,
)
from webauthn.helpers.structs import (
    PublicKeyCredentialDescriptor,
    UserVerificationRequirement,
    AuthenticationCredential,
)

from classquiz.oauth.authenticate_user import log_user_in

settings = settings()
router = APIRouter()


class StartLoginInput(BaseModel):
    email: str


class StartLoginResponseTypes(enum.Enum):
    PASSWORD = "PASSWORD"
    PASSKEY = "PASSKEY"
    TOTP = "TOTP"
    BACKUP = "BACKUP"


class LoginSession(BaseModel):
    user_id: str
    step_1: set[StartLoginResponseTypes]
    step_2: set[StartLoginResponseTypes]
    webauthn_challenge: str | None = None
    step1_success: bool = False


class StartLoginResponse(BaseModel):
    step_1: set[StartLoginResponseTypes]
    step_2: set[StartLoginResponseTypes]
    session_id: str
    webauthn_data: None | str = None


def verify_webauthn(data, fidocredentialss: list[FidoCredentials], login_session: LoginSession):
    try:
        credential = AuthenticationCredential.parse_obj(data)
    except ValidationError:
        print("ValidationError")
        raise HTTPException(401)

    user_cred: FidoCredentials | None = None

    credential.id = base64url_to_bytes(credential.id)
    for cred in fidocredentialss:
        if cred.id == credential.id:
            user_cred = cred
            break
    if user_cred is None:
        print("user_cred not in DB")
        raise HTTPException(401)
    credential.id = base64.urlsafe_b64encode(credential.raw_id).decode("utf-8").replace("=", "")
    credential.response.client_data_json = base64.b64decode(credential.response.client_data_json + b"==")
    credential.response.authenticator_data = base64.urlsafe_b64decode(credential.response.authenticator_data + b"==")
    credential.response.signature = base64.urlsafe_b64decode(credential.response.signature + b"==")
    try:
        verify_authentication_response(
            credential=credential,
            expected_challenge=base64.b64decode(login_session.webauthn_challenge),
            expected_rp_id=urllib.parse.urlparse(settings.root_address).hostname,
            expected_origin=settings.root_address,
            credential_public_key=user_cred.public_key,
            credential_current_sign_count=user_cred.sign_count,
            require_user_verification=False,
        )
        print("logging in...")
        return True
    except Exception as err:
        print(err)
        raise HTTPException(status_code=401)


@router.post("/start")
async def start_login(data: StartLoginInput):
    user = (
        await User.objects.select_related("fidocredentialss")
        .filter((User.email == data.email) | (User.username == data.email))
        .get_or_none()
    )
    step_1: set[StartLoginResponseTypes] = set()
    step_2: set[StartLoginResponseTypes] = set()
    webauthn_data = None
    webauthn_challenge = None
    if user is None or not user.verified:
        step_1.add(StartLoginResponseTypes.PASSWORD)
        return StartLoginResponse(step_1=step_1, step_2=step_2, session_id=os.urandom(16).hex(), webauthn_data=None)
    if user.password is not None:
        step_1.add(StartLoginResponseTypes.PASSWORD)
    if len(user.fidocredentialss) > 0:
        if user.require_password is True:
            step_2.add(StartLoginResponseTypes.PASSKEY)
        else:
            step_1.add(StartLoginResponseTypes.PASSKEY)
        webauthn_data = generate_authentication_options(
            rp_id=urllib.parse.urlparse(settings.root_address).hostname,
            allow_credentials=[
                PublicKeyCredentialDescriptor(id=cred.id, type="public-key") for cred in user.fidocredentialss
            ],
            user_verification=UserVerificationRequirement.PREFERRED,
        )
        webauthn_challenge = base64.b64encode(webauthn_data.challenge).decode("utf-8")
        webauthn_data = options_to_json(webauthn_data)
    if user.totp_secret is not None:
        if user.require_password:
            step_2.add(StartLoginResponseTypes.TOTP)
        else:
            step_1.add(StartLoginResponseTypes.TOTP)
    login_session = LoginSession(
        step_1=step_1,
        step_2=step_2,
        user_id=user.id.hex,
        webauthn_challenge=webauthn_challenge,
    )
    session_id = os.urandom(16).hex()
    await redis.set(f"login_session:{session_id}", login_session.json(), ex=600)
    return StartLoginResponse(step_1=step_1, step_2=step_2, session_id=session_id, webauthn_data=webauthn_data)


class StepInput(BaseModel):
    auth_type: StartLoginResponseTypes
    data: str | dict


@router.post("/step/{step_id}")
async def step_1_endpoint(session_id: str, data: StepInput, request: Request, response: Response, step_id: int):
    if step_id < 0 or step_id > 2:
        raise HTTPException(status_code=401)
    redis_res = await redis.get(f"login_session:{session_id}")
    if redis_res is None:
        raise HTTPException(401, detail="wrong credentials")
    login_session = LoginSession.parse_raw(redis_res)

    if step_id == 1:
        if data.auth_type not in {*login_session.step_1, StartLoginResponseTypes.BACKUP}:
            print("AUTH_TYPE not in data")
            raise HTTPException(401)
    elif step_id == 2:
        if data.auth_type not in login_session.step_2:
            print("AUTH_TYPE not in data")
            raise HTTPException(401)
    else:
        print("unknown step")
        raise HTTPException(401)
    user = await User.objects.select_related("fidocredentialss").get_or_none(id=uuid.UUID(login_session.user_id))
    if data.auth_type == StartLoginResponseTypes.PASSWORD:
        if verify_password(data.data, user.password):
            if len(login_session.step_2) == 0 or (step_id == 2 and login_session.step1_success is True):
                return await log_user_in(user, request, response)
            else:
                login_session.step1_success = True
                await redis.set(f"login_session:{session_id}", login_session.json(), ex=600)
                return Response(status_code=202)
        else:
            print("Wrong Password")
            raise HTTPException(401, detail="wrong credentials")
    elif data.auth_type == StartLoginResponseTypes.PASSKEY:
        res = verify_webauthn(data=data.data, fidocredentialss=user.fidocredentialss, login_session=login_session)
        if res is True:
            if len(login_session.step_2) == 0 or (step_id == 2 and login_session.step1_success is True):
                return await log_user_in(user, request, response)
            else:
                login_session.step1_success = True
                await redis.set(f"login_session:{session_id}", login_session.json(), ex=600)
                return Response(status_code=202)
        else:
            raise HTTPException(401, detail="webauthn failed")
    elif data.auth_type == StartLoginResponseTypes.BACKUP:
        if user.backup_code == data.data:
            user.backup_code = os.urandom(32).hex()
            await user.update()
            return await log_user_in(user, request, response)
        else:
            print("Wrong Backup-Code")
            raise HTTPException(status_code=401)
    elif data.auth_type == StartLoginResponseTypes.TOTP:
        if step_id == 1 and user.require_password:
            print("TOTP Cant be step 1")
            raise HTTPException(401)
        totp = pyotp.TOTP(user.totp_secret)
        if totp.verify(data.data):
            return await log_user_in(user, request, response)
        else:
            raise HTTPException(401, detail="totp wrong")
