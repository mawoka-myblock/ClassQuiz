#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

import io
import os

import aiofiles
import aiofiles.os


class LocalStorage:
    def __init__(self, base_path: str):
        self.base_path = base_path

    async def get_file(self, file_name: str) -> io.BytesIO | None:
        try:
            async with aiofiles.open(file=os.path.join(self.base_path, file_name), mode="rb") as f:
                return io.BytesIO(await f.read())
        except FileNotFoundError:
            return None

    async def write_file(self, file_name: str, data: bytes) -> None:
        async with aiofiles.open(file=os.path.join(self.base_path, file_name), mode="wb") as f:
            await f.write(data)

    async def delete_file(self, file_names: [str]) -> None:
        for i in file_names:
            try:
                await aiofiles.os.remove(os.path.join(self.base_path, i))
            except FileNotFoundError:
                pass
        return None
