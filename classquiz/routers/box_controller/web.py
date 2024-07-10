# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import os
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from classquiz.auth import get_current_user
from classquiz.db.models import User, Controller
from classquiz.config import redis
from classquiz.helpers.box_controller import generate_code

router = APIRouter()


class SetControllerUpInput(BaseModel):
    player_name: str | None = None
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
    data = Controller(
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


GetControllerResponse = Controller.get_pydantic(exclude={"secret_key", "user"})


@router.get("/controller")
async def get_controller(id: uuid.UUID, user: User = Depends(get_current_user)) -> GetControllerResponse:
    controller = await Controller.objects.get_or_none(id=id, user=user.id)
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
    controller = await Controller.objects.get_or_none(id=data.id, user=user.id)
    if controller is None:
        raise HTTPException(status_code=404, detail="Controller not found")
    controller.player_name = data.player_name
    controller.name = data.name
    await controller.update()
    return GetControllerResponse(**controller.dict())


@router.get("/list")
async def get_all_controllers(user: User = Depends(get_current_user)) -> list[GetControllerResponse]:
    controllers = await Controller.objects.all(user=user.id)
    if len(controllers) == 0:
        return []
    return_list = []
    for controller in controllers:
        return_list.append(GetControllerResponse(**controller.dict()))
    return return_list


class SetVersionToBeFlashedInput(BaseModel):
    id: uuid.UUID
    version: str


@router.post("/set_update")
async def set_version_to_be_flashed(data: SetVersionToBeFlashedInput, user: User = Depends(get_current_user)):
    controller = await Controller.objects.get_or_none(id=data.id, user=user.id)
    if controller is None:
        raise HTTPException(status_code=404, detail="Controller not found")
    controller.wanted_os_version = data.version
    await controller.update()
