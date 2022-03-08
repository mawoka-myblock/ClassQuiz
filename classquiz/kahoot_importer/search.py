from uuid import UUID
from typing import List, Any, Optional
from aiohttp import ClientSession
from classquiz.kahoot_importer import _Entity

from pydantic import BaseModel


class _Response(BaseModel):
    entities: List[_Entity]
    totalHits: int
    cursor: int
    pageTimestamp: int


async def search(query: str | None, limit: int | None = 9, cursor: int | None = 1,
                 search_cluster: int | None = 1, inventory_item_id: str | None = "ANY") -> _Response:
    """

    :param inventory_item_id: I dkon't know
    :param search_cluster: Doesn't seeem to matter
    :param cursor: The position in the result-list (page)
    :param query: The search query
    :param limit: Less or equals 100
    :return:
    """
    async with ClientSession() as session:
        async with session.get(
                f"https://create.kahoot.it/rest/kahoots/?query={query}&limit={limit}&cursor={cursor}&searchCluster={search_cluster}&includeExtendedCounters=false&inventoryItemId={inventory_item_id}"

        ) as response:
            # print(
            #    f"https://create.kahoot.it/rest/kahoots/?query={query}&limit={limit}&cursor={cursor}&searchCluster={search_cluster}&includeExtendedCounters=false&inventoryItemId={inventory_item_id}")
            return _Response(**await response.json())
