#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import os
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from classquiz.auth import get_current_user
from classquiz.db.models import User, Controllers
from classquiz.config import redis
from classquiz.helpers.box_controller import generate_code

router = APIRouter()


class SetControllerUpInput(BaseModel):
    player_name: str | None
    name: str


class SetControllerUpResponse(BaseModel):
    code: str
    id: uuid.UUID


@router.post("/setup")
async def set_controller_up(
    input_data: SetControllerUpInput, user: User = Depends(get_current_user)
) -> SetControllerUpResponse:
    code = generate_code(10)
    if input_data.player_name is None:
        input_data.player_name = user.username
    data = Controllers(
        id=uuid.uuid4(),
        user=user,
        secret_key=os.urandom(12).hex(),
        player_name=input_data.player_name,
        last_seen=None,
        first_seen=None,
        name=input_data.name,
        os_version=None,
    )
    await data.save()
    await redis.set(f"controller_setup:{code}", data.id.hex, ex=900)
    return SetControllerUpResponse(code=code, id=data.id)


GetControllerResponse = Controllers.get_pydantic(exclude={"secret_key", "user"})


@router.get("/controller")
async def get_controller(id: uuid.UUID, user: User = Depends(get_current_user)) -> GetControllerResponse:
    controller = await Controllers.objects.get_or_none(id=id, user=user.id)
    if controller is None:
        raise HTTPException(status_code=404, detail="Controller not found")
    return GetControllerResponse(**controller.dict())


class ModifyControllerInput(BaseModel):
    id: uuid.UUID
    player_name: str
    name: str


@router.post("/modify")
async def modify_controller(
    data: ModifyControllerInput, user: User = Depends(get_current_user)
) -> GetControllerResponse:
    controller = await Controllers.objects.get_or_none(id=data.id, user=user.id)
    if controller is None:
        raise HTTPException(status_code=404, detail="Controller not found")
    controller.player_name = data.player_name
    controller.name = data.name
    await controller.update()
    return GetControllerResponse(**controller.dict())
