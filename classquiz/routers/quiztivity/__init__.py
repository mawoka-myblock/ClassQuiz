# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException

from classquiz.auth import get_current_user
from datetime import datetime
from classquiz.db.models import User, QuizTivityInput, QuizTivity, QuizTivityShare, PublicQuizTivityShare
from classquiz.routers.quiztivity.shares import router as shares_router

router = APIRouter()

router.include_router(shares_router, prefix="/shares")


@router.post("/create", response_model_exclude={"user": ...})
async def create_quiztivity(data: QuizTivityInput, user: User = Depends(get_current_user)) -> QuizTivity:
    quiztivity = QuizTivity.parse_obj({**data.dict(), "user": user, "id": uuid4(), "created_at": datetime.now()})
    return await quiztivity.save()


@router.get("/{uuid}", response_model_exclude={"user": ...})
async def get_quiztivity(uuid: UUID) -> QuizTivity:
    quiztivity = await QuizTivity.objects.get_or_none(id=uuid)
    if quiztivity is None:
        raise HTTPException(status_code=404, detail="QuizTivity not found")
    return quiztivity


@router.put("/{uuid}", response_model_exclude={"user": ...})
async def put_quiztivity(data: QuizTivityInput, uuid: UUID, user: User = Depends(get_current_user)) -> QuizTivity:
    quiztivity = await QuizTivity.objects.get_or_none(id=uuid, user=user)
    if quiztivity is None:
        raise HTTPException(status_code=404, detail="QuizTivity not found")
    quiztivity.pages = data.dict()["pages"]
    quiztivity.title = data.title
    return await quiztivity.update()


@router.delete("/{uuid}")
async def delete_quiztivity(uuid: UUID):
    quiztivity = await QuizTivity.objects.get_or_none(id=uuid)
    if quiztivity is None:
        raise HTTPException(status_code=404, detail="QuizTivity not found")
    await quiztivity.delete()


@router.get("/")
async def get_all_quiztivities(user: User = Depends(get_current_user)) -> list[QuizTivity]:
    quiztivities = await QuizTivity.objects.filter(user=user).order_by(QuizTivity.created_at.desc()).all()
    return quiztivities


@router.get("/{uuid}/shares")
async def get_shares(uuid: UUID, user: User = Depends(get_current_user)) -> list[PublicQuizTivityShare]:
    shares = (
        await QuizTivityShare.objects.filter(quiztivity=uuid, user=user).order_by(QuizTivityShare.expire_at.asc()).all()
    )
    resp_shares = []
    for share in shares:
        resp_shares.append(PublicQuizTivityShare.from_db_model(share))
    return resp_shares
