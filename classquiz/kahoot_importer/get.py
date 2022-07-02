#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

from aiohttp import ClientSession
from pydantic import BaseModel

from classquiz.kahoot_importer import _Card, _Kahoot


class _Response(BaseModel):
    card: _Card
    kahoot: _Kahoot


async def get(game_id: str) -> _Response | None:
    async with ClientSession() as session, session.get(
        f"https://create.kahoot.it/rest/kahoots/{game_id}/card/?includeKahoot=true"
    ) as response:
        if response.status == 200:
            return _Response(**await response.json())
        elif response.status == 404:
            return None
        elif response.status == 400:
            return None
        elif response.status == 403:
            return None
        else:
            raise Exception(f"Unexpected response status: {response.status}")
