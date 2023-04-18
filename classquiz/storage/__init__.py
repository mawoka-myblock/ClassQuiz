#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

from io import BytesIO
from typing import Optional

from .deta_storage import DetaStorage
from .local_storage import LocalStorage
from .s3_storage import S3Storage


class Storage:
    def __init__(
        self,
        backend: str,
        deta_key: Optional[str],
        deta_id: Optional[str],
        storage_path: Optional[str],
        access_key: str | None = None,
        secret_key: str | None = None,
        bucket_name: str | None = None,
        base_url: str | None = None,
    ):
        self.backend = backend
        self.deta_key: str | None = deta_key
        self.deta_id: str | None = deta_id
        # self.deta_base_url = f"https://drive.deta.sh/v1/{deta_id}/classquiz1"
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.base_url = base_url
        self.deta_instance = None
        if backend == "deta":
            if deta_key is None or deta_id is None:
                raise ValueError("deta_key and deta_id must be provided")
            if self.base_url is None:
                self.base_url = f"https://drive.deta.sh/v1/{deta_id}/classquiz1"
            self.deta_instance = DetaStorage(
                deta_base_url=self.base_url,
                deta_key=self.deta_key,
                deta_id=self.deta_id,
            )

        elif backend == "local":
            if storage_path is None:
                raise ValueError("storage_path must be provided")
            else:
                self.local_instance = LocalStorage(base_path=storage_path)

        elif backend == "s3":
            if access_key is None or secret_key is None or bucket_name is None or base_url is None:
                raise ValueError("Not all parameters given")
            self.s3_instance = S3Storage(
                base_url=base_url, access_key=access_key, secret_key=secret_key, bucket_name=bucket_name
            )

        else:
            raise NotImplementedError(f"Backend {backend} not implemented")

    async def download(self, file_name: str) -> BytesIO | None:
        if self.backend == "deta":
            return await self.deta_instance.download(file_name)
        elif self.backend == "local":
            return await self.local_instance.get_file(file_name)
        elif self.backend == "s3":
            return await self.s3_instance.download(file_name)

    async def upload(self, file_name: str, file_data: bytes) -> None:
        if self.backend == "deta":
            return await self.deta_instance.upload(file=file_data, file_name=file_name)
        elif self.backend == "local":
            return await self.local_instance.write_file(file_name=file_name, data=file_data)
        elif self.backend == "s3":
            return await self.s3_instance.upload(file=file_data, file_name=file_name)

    async def delete(self, file_names: [str]) -> None:
        if self.backend == "deta":
            return await self.deta_instance.delete(file_names=file_names)
        elif self.backend == "local":
            return await self.local_instance.delete_file(file_names=file_names)
        elif self.backend == "s3":
            return await self.s3_instance.delete(file_names=file_names)

    async def get_url(self, file_name: str, expiry: int) -> str:
        if self.backend == "s3":
            return self.s3_instance.get_url(file_name=file_name, expire=expiry)
