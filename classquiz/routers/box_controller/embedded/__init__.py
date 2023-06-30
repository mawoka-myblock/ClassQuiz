# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import os
import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from classquiz.config import redis
from classquiz.db.models import PlayGame, Controller
from classquiz.routers.box_controller.embedded.socket import router as socket_router

router = APIRouter()
router.include_router(socket_router, prefix="/socket")


class JoinGameInput(BaseModel):
    id: uuid.UUID
    secret_key: str
    code: str


class JoinGameResponse(BaseModel):
    id: str


@router.post("/join")
async def join_game(data: JoinGameInput) -> JoinGameResponse:
    controller = await Controller.objects.get_or_none(id=data.id, secret_key=data.secret_key)
    game_pin = await redis.get(f"game:cqc:code:{data.code}")
    if game_pin is None:
        raise HTTPException(status_code=404, detail="Game not found")
    game = await redis.get(f"game:{game_pin}")
    game = PlayGame.parse_raw(game)
    # Check if game is already running
    if game.started:
        raise HTTPException(status_code=400, detail="Game started already")
    # check if username already exists
    if await redis.get(f"game_session:{game_pin}:players:{controller.player_name}") is not None:
        raise HTTPException(status_code=409, detail="Username already exists")

    player_id = os.urandom(5).hex()
    await redis.set(f"game:cqc:player:{player_id}", controller.player_name)
    return JoinGameResponse(id=f"{player_id}:{game_pin}")


class RegisterWithCodeInput(BaseModel):
    code: str


class RegisterWithCodeResponse(BaseModel):
    id: uuid.UUID
    secret_key: str


@router.post("/register")
async def register_with_code(data: RegisterWithCodeInput) -> RegisterWithCodeResponse:
    c_id = await redis.get(f"controller_setup:{data.code}")
    if c_id is None:
        raise HTTPException(status_code=404, detail="Code not found")
    await redis.delete(f"controller_setup:{data.code}")
    c_id = uuid.UUID(c_id)
    controller = await Controller.objects.get(id=c_id)
    controller.first_seen = datetime.now()
    controller.last_seen = datetime.now()
    await controller.update()
    return RegisterWithCodeResponse(id=controller.id, secret_key=controller.secret_key)


@router.get("/ping")
async def ping_server(id: uuid.UUID, secret_key: str, version: str):
    controller = await Controller.objects.get_or_none(id=id, secret_key=secret_key)
    if controller is None:
        raise HTTPException(status_code=404, detail="Key and/or id invalid")
    controller.last_seen = datetime.now()
    controller.os_version = version
    await controller.update()


@router.get("/update")
async def get_firmware_version(id: uuid.UUID, secret_key: str) -> PlainTextResponse:
    controller = await Controller.objects.get_or_none(id=id, secret_key=secret_key)
    if controller is None:
        return PlainTextResponse(status_code=404, content="Key and/or id invalid")
    if controller.wanted_os_version is None:
        return PlainTextResponse(status_code=400, content="No update needed")
    return PlainTextResponse(status_code=200, content=controller.wanted_os_version)
