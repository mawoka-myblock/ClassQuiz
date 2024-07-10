# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta

from classquiz.auth import get_current_user
from classquiz.db.models import User, QuizTivityShare, QuizTivity, PublicQuizTivityShare

router = APIRouter()


@router.get("/")
async def get_shares(user: User = Depends(get_current_user)) -> list[PublicQuizTivityShare]:
    shares = await QuizTivityShare.objects.filter(user=user).all()
    resp_shares = []
    for share in shares:
        resp_shares.append(PublicQuizTivityShare.from_db_model(share))
    return resp_shares


class CreateShareInput(BaseModel):
    name: str | None = None
    quiztivity: UUID
    expire_in: int | None = None


@router.post("/")
async def create_share(data: CreateShareInput, user: User = Depends(get_current_user)) -> PublicQuizTivityShare:
    quiztivity = await QuizTivity.objects.get_or_none(id=data.quiztivity, user=user)
    expire_at = None
    if data.expire_in is not None:
        expire_at = (datetime.now() + timedelta(minutes=data.expire_in)).replace(tzinfo=None)
    if quiztivity is None:
        raise HTTPException(status_code=400, detail="Quiztivity wasn't found")
    share = await QuizTivityShare.objects.create(
        id=uuid4(), name=data.name, expire_at=expire_at, quiztivity=quiztivity, user=user
    )
    share = PublicQuizTivityShare.from_db_model(share)
    return share


@router.delete("/{uuid}")
async def delete_share(uuid: UUID, user: User = Depends(get_current_user)):
    share = await QuizTivityShare.objects.get_or_none(id=uuid, user=user)
    if share is None:
        raise HTTPException(status_code=404, detail="Share wasn't found")
    await share.delete()
    return


class UpdateShareInput(BaseModel):
    name: str | None = None
    expire_in: int | None = None


@router.put("/{uuid}")
async def update_share(
    data: UpdateShareInput, uuid: UUID, user: User = Depends(get_current_user)
) -> PublicQuizTivityShare:
    share = await QuizTivityShare.objects.get_or_none(id=uuid, user=user)
    if share is None:
        raise HTTPException(status_code=404, detail="Share wasn't found")
    expire_at = None
    if data.expire_in is not None:
        expire_at = (datetime.now() + timedelta(minutes=data.expire_in)).replace(tzinfo=None)
    share.name = data.name
    share.expire_at = expire_at
    return PublicQuizTivityShare.from_db_model(await share.update())


@router.get("/{uuid}")
async def get_share(uuid: UUID) -> QuizTivity:
    share = await QuizTivityShare.objects.select_related("quiztivity").get_or_none(id=uuid)
    if share is None:
        raise HTTPException(status_code=404, detail="Share not found")
    if share.expire_at is None:
        return share.quiztivity
    if share.expire_at < datetime.now():
        raise HTTPException(status_code=410, detail="Already expired")
    return share.quiztivity
