import io
import os
import aiofiles


class LocalStorage:
    def __init__(self, base_path: str):
        self.base_path = base_path

    async def get_file(self, file_name: str) -> io.BytesIO:
        async with aiofiles.open(file=os.path.join(self.base_path, file_name), mode='rb') as f:
            return io.BytesIO(await f.read())

    async def write_file(self, file_name: str, data: bytes) -> None:
        async with aiofiles.open(file=os.path.join(self.base_path, file_name), mode='wb') as f:
            await f.write(data)

