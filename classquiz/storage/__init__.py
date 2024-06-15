# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


from typing import Optional, BinaryIO

from .local_storage import LocalStorage
from .s3_storage import S3Storage
from typing import Generator


class Storage:
    def __init__(
        self,
        backend: str,
        storage_path: Optional[str],
        access_key: str | None = None,
        secret_key: str | None = None,
        bucket_name: str | None = None,
        base_url: str | None = None,
    ):
        self.backend = backend
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.base_url = base_url
        self.instance: LocalStorage | S3Storage | None = None

        if backend == "local":
            if storage_path is None:
                raise ValueError("storage_path must be provided")
            else:
                self.instance = LocalStorage(base_path=storage_path)

        elif backend == "s3":
            if access_key is None or secret_key is None or bucket_name is None or base_url is None:
                raise ValueError("Not all parameters given")
            self.instance = S3Storage(
                base_url=base_url, access_key=access_key, secret_key=secret_key, bucket_name=bucket_name
            )

        else:
            raise NotImplementedError(f"Backend {backend} not implemented")

    def download(self, file_name: str) -> Generator | None:
        return self.instance.download(file_name)

    async def upload(
        self, file_name: str, file_data: BinaryIO, mime_type: str | None = None, size: int | None = None
    ) -> None:
        return await self.instance.upload(file=file_data, file_name=file_name, mime_type=mime_type, size=size)

    async def delete(self, file_names: [str]) -> None:
        return await self.instance.delete(file_names=file_names)

    async def get_url(self, file_name: str, expiry: int) -> str:
        if self.backend == "s3":
            return self.instance.get_url(file_name=file_name, expire=expiry)

    async def get_file_size(self, file_name: str) -> int | None:
        return self.instance.size(file_name)
