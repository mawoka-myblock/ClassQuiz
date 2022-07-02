#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

from io import BytesIO
from classquiz.storage.errors import DeletionFailedError, SavingFailedError, DownloadingFailedError

from aiohttp import ClientSession


class DetaStorage:
    def __init__(self, deta_base_url: str, deta_id: str, deta_key: str):
        self.deta_url = deta_base_url
        self.deta_id = deta_id
        self.deta_key = deta_key
        self.headers = {
            "X-Api-Key": self.deta_key,
        }

    async def download(self, file_name: str) -> BytesIO | None:
        """

        :param file_name: The name of the file to be downloaded
        :return: Either bytes f successfull download or None if failed
        """
        async with ClientSession(headers=self.headers) as session, session.get(
            f"{self.deta_url}/files/download?name={file_name}"
        ) as response:
            if response.status == 200:
                return BytesIO(await response.read())
            elif response.status == 404:
                return None
            else:
                raise DownloadingFailedError

    async def upload(self, file: bytes, file_name: str) -> None:
        """
        :param file: The file in bytes
        :param file_name: The name of the file
        :return:
        """
        async with ClientSession(headers=self.headers) as session, session.post(
            f"{self.deta_url}/files?name={file_name}", data=file
        ) as response:
            if response.status == 201:
                return None
            else:
                print(response.status, await response.json())
                raise SavingFailedError

    async def delete(self, file_names: [str]) -> None:
        async with ClientSession(headers=self.headers) as session, session.delete(
            f"{self.deta_url}/files", json={"names": file_names}
        ) as response:
            if response.status == 200:
                return None
            else:
                raise DeletionFailedError
