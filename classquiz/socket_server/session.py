# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0

from classquiz.config import redis
import json
from typing import Any
from socketio import AsyncServer
from socketio.exceptions import ConnectionRefusedError


async def get_session(sid: str, sio: AsyncServer, disconnect_on_error: bool = True) -> dict:
    session_id = (await sio.get_session(sid)).get("session_id")
    if session_id is None:
        raise ConnectionRefusedError("Session not configured")
    val = await redis.get(f"socket_io_session:{session_id}")
    if disconnect_on_error and val is None:
        raise ConnectionRefusedError("session not available")
    return json.loads(val)


async def save_session(sid: str, sio: AsyncServer, data: Any, disconnect_on_error: bool = True) -> None:
    session_id = (await sio.get_session(sid)).get("session_id")
    if session_id is None:
        raise ConnectionRefusedError("Session not configured")
    await redis.set(f"socket_io_session:{session_id}", json.dumps(data), ex=3600)
