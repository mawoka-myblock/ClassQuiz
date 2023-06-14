#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os
from typing import BinaryIO, Generator

import aiofiles
import aiofiles.os

_DEFAULT_CHUNK_SIZE = 32768  # bytes; arbitrary


async def aioshutil_copyfileobj(async_fsrc, async_fdst, *, chunksize: int = _DEFAULT_CHUNK_SIZE) -> None:
    while (chunk := await async_fsrc.read(chunksize)) != b"":
        await async_fdst.write(chunk)


class LocalStorage:
    def __init__(self, base_path: str):
        self.base_path = base_path

    async def download(self, file_name: str) -> Generator | None:
        try:
            async with aiofiles.open(file=os.path.join(self.base_path, file_name), mode="rb") as f:
                yield f.read()
        except FileNotFoundError:
            yield None

    # skipcq: PYL-W0613
    async def upload(self, file_name: str, file: BinaryIO, mime_type: str | None = None) -> None:
        async with aiofiles.open(file=os.path.join(self.base_path, file_name), mode="wb") as f:
            await aioshutil_copyfileobj(file, f)

    async def delete(self, file_names: [str]) -> None:
        for i in file_names:
            try:
                await aiofiles.os.remove(os.path.join(self.base_path, i))
            except FileNotFoundError:
                pass
        return None

    def size(self, file_name: str) -> int | None:
        try:
            return os.stat(os.path.join(self.base_path, file_name))
        except FileNotFoundError:
            return None
