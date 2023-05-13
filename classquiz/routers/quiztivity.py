#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException

from classquiz.auth import get_current_user
from datetime import datetime
from classquiz.db.models import User, QuizTivityInput, QuizTivity

router = APIRouter()


@router.post("/create")
async def create_quiztivity(data: QuizTivityInput, user: User = Depends(get_current_user)) -> QuizTivity:
    quiztivity = QuizTivity.parse_obj({**data.dict(), "user": user, "id": uuid4(), "created_at": datetime.now()})
    return await quiztivity.save()


@router.get("/{uuid}")
async def get_quiztivity(uuid: UUID) -> QuizTivity:
    quiztivity = await QuizTivity.objects.get_or_none(id=uuid)
    if quiztivity is None:
        raise HTTPException(status_code=404, detail="QuizTivity not found")
    return quiztivity


@router.put("/{uuid}")
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
