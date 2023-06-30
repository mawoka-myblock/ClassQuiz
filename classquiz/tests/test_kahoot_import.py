# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import pytest

from classquiz.kahoot_importer.import_quiz import _download_image

ddg_robots_txt = b"""a"""
test_url = (
    "https://gist.githubusercontent.com/mawoka-myblock/b43f0d888a9e6a25806b3c73e63b658f/raw"
    "/134f135f99f8f385695304f739667c70b636386a/test-gist"
)


@pytest.mark.asyncio
async def test_download_image():
    image = await _download_image(test_url)
    assert image == ddg_robots_txt
