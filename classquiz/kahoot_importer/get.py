from aiohttp import ClientSession

from pydantic import BaseModel
from classquiz.kahoot_importer import _Card, _Kahoot


class _Response(BaseModel):
    card: _Card
    kahoot: _Kahoot


async def get(game_id: str) -> _Response:
    async with ClientSession() as session:
        async with session.get(f"https://create.kahoot.it/rest/kahoots/{game_id}/card/?includeKahoot=true") as response:
            return _Response(**await response.json())
