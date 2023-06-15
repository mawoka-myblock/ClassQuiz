#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import random

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from classquiz.auth import get_current_user
from classquiz.db.models import User, PlayGame
from classquiz.config import redis

router = APIRouter()


def generate_code() -> str:
    specified_length = 6
    buttons = [
        "B",
        "b",
        "G",
        "g",
        "Y",
        "y",
        "R",
        "r",
    ]  # Capital stands for long press, lowercase letter for short press
    resulting_code = ""
    for _ in range(specified_length):
        resulting_code += random.choice(buttons)
    return resulting_code


class ActivateCqbForCurrentQuizInput(BaseModel):
    game_pin: int


class ActivateCqbForCurrentQuizResponse(BaseModel):
    code: str


@router.post("/activate-for-quiz", response_model=ActivateCqbForCurrentQuizResponse)
async def activate_cqc_for_current_quiz(data: ActivateCqbForCurrentQuizInput, user: User = Depends(get_current_user)):
    redis_res = await redis.get(f"game:{data.game_pin}")
    if redis_res is None:
        raise HTTPException(status_code=404, detail="Game not found")
    game_data = PlayGame.parse_raw(redis_res)
    if game_data.user_id != user.id:
        raise HTTPException(status_code=401, detail="The quiz wasn't started by you")
    code = generate_code()
    await redis.set(f"game:cqc:code:{code}", game_data.game_pin, ex=3600)
    return ActivateCqbForCurrentQuizResponse(code=code)
