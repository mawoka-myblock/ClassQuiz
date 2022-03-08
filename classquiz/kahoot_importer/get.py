from aiohttp import ClientSession

from pydantic import BaseModel
from classquiz.kahoot_importer import _Card, _Kahoot


class _Response(BaseModel):
    card: _Card
    kahoot: _Kahoot


async def get(game_id: str) -> _Response | None:
    async with ClientSession() as session:
        async with session.get(f"https://create.kahoot.it/rest/kahoots/{game_id}/card/?includeKahoot=true") as response:
            if response.status == 200:
                return _Response(**await response.json())
            elif response.status == 404:
                return None
            else:
                raise Exception(f"Unexpected response status: {response.status}")
