# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


from typing import List

from aiohttp import ClientSession
from pydantic import BaseModel

from classquiz.kahoot_importer import _Entity


# noqa : E501
class _Response(BaseModel):
    entities: List[_Entity]
    totalHits: int
    cursor: int | None = None
    pageTimestamp: int


async def search(
    query: str | None = None,
    limit: int | None = 9,
    cursor: int | None = 1,
    search_cluster: int | None = 1,
    inventory_item_id: str | None = "ANY",
) -> _Response:
    """

    :param inventory_item_id: I dkon't know
    :param search_cluster: Doesn't seeem to matter
    :param cursor: The position in the result-list (page)
    :param query: The search query
    :param limit: Less or equals 100
    :return:
    """
    async with (
        ClientSession() as session,
        session.get(
            f"https://create.kahoot.it/rest/kahoots/?query={query}&limit={limit}&cursor={cursor}&searchCluster={search_cluster}&includeExtendedCounters=false&inventoryItemId={inventory_item_id}"  # noqa : E501
        ) as response,
    ):
        return _Response(**await response.json())
