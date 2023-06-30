# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import os
import urllib.parse

import pyotp
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from classquiz.auth import get_current_user
from classquiz.db.models import User

router = APIRouter()


class GetBackupCodeResponse(BaseModel):
    code: str


@router.get("/backup_code", response_model=GetBackupCodeResponse)
async def get_backup_code(user: User = Depends(get_current_user)):
    backup_code = os.urandom(32).hex()
    user = await User.objects.get(id=user.id)
    user.backup_code = backup_code
    await user.update()
    return GetBackupCodeResponse(code=backup_code)


class SetRequirePassword(BaseModel):
    require_password: bool


@router.post("/require_password", response_model=SetRequirePassword)
async def set_require_password(data: SetRequirePassword, user: User = Depends(get_current_user)):
    user = await User.objects.get(id=user.id)
    user.require_password = data.require_password
    await user.update()
    return data


class SetTotpUpResponse(BaseModel):
    url: str
    secret: str


@router.post("/totp", response_model=SetTotpUpResponse)
async def set_totp_up(user: User = Depends(get_current_user)):
    user = await User.objects.get(id=user.id)
    user.totp_secret = pyotp.random_base32()
    url = pyotp.totp.TOTP(user.totp_secret).provisioning_uri(
        name=urllib.parse.quote(user.username), issuer_name="ClassQuiz"
    )
    await user.update()
    return SetTotpUpResponse(url=url, secret=user.totp_secret)


class GetTotpStatusResponse(BaseModel):
    activated: bool


@router.get("/totp", response_model=GetTotpStatusResponse)
async def get_totp_status(user: User = Depends(get_current_user)):
    user = await User.objects.get(id=user.id)
    if user.totp_secret is None:
        return GetTotpStatusResponse(activated=False)
    else:
        return GetTotpStatusResponse(activated=True)


@router.delete("/totp")
async def disable_totp(user: User = Depends(get_current_user)):
    user = await User.objects.get(id=user.id)
    user.totp_secret = None
    await user.update()
