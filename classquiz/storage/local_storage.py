# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import os
from shutil import copyfileobj
from typing import BinaryIO, Generator

import aiofiles
import aiofiles.os

_DEFAULT_CHUNK_SIZE = 32768  # bytes; arbitrary


class LocalStorage:
    def __init__(self, base_path: str):
        self.base_path = base_path

    async def download(self, file_name: str) -> Generator | None:
        try:
            async with aiofiles.open(file=os.path.join(self.base_path, file_name), mode="rb") as f:
                while True:
                    chunk = await f.read(8192)
                    if not chunk:
                        break
                    yield chunk
        except FileNotFoundError:
            yield None

    # skipcq: PYL-W0613
    async def upload(
        self,
        file_name: str,
        file: BinaryIO,
        size: int | None,
        mime_type: str | None = None,
    ) -> None:
        with open(file=os.path.join(self.base_path, file_name), mode="wb") as f:
            copyfileobj(file, f)

    async def delete(self, file_names: [str]) -> None:
        for i in file_names:
            try:
                await aiofiles.os.remove(os.path.join(self.base_path, i))
            except FileNotFoundError:
                pass
        return None

    def size(self, file_name: str) -> int | None:
        try:
            return os.stat(os.path.join(self.base_path, file_name)).st_size
        except FileNotFoundError:
            return None
