# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import pytest

from classquiz.kahoot_importer.search import search


@pytest.mark.asyncio
@pytest.mark.order(-2)
async def test_search():
    res = await search(query="Python", limit=100)
    assert len(res.entities) == 100
    await search(query="Test Quiz", limit=100)
    await search(query="Biologie", limit=100)
    await search(query="Chemie", limit=100)
    await search(query="Deutsch", limit=100)
    await search(query="Mathe", limit=100)
    await search(query="Englisch", limit=100)
    await search(query="Barbie", limit=100)
    await search(query="Internet", limit=100)
    await search(query="Windows", limit=100)
    await search(query="Python", limit=100)
