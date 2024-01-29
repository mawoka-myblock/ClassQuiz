# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


from aiohttp import ClientSession
from pydantic import BaseModel

from classquiz.kahoot_importer import _Card, _Kahoot


class _Response(BaseModel):
    card: _Card
    kahoot: _Kahoot


async def get(game_id: str) -> _Response | int:
    async with (
        ClientSession() as session,
        session.get(f"https://create.kahoot.it/rest/kahoots/{game_id}/card/?includeKahoot=true") as response,
    ):
        if response.status == 200:
            return _Response(**await response.json())
        else:
            return response.status
