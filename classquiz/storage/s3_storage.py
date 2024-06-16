# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Tuple, BinaryIO, Generator

from aiohttp import ClientSession
import minio
from pydantic import BaseModel
from classquiz.storage.errors import DeletionFailedError, SavingFailedError, DownloadingFailedError


class S3Storage:
    class _HeaderAndParams(BaseModel):
        params: dict[str, str]
        headers: dict[str, str]

    def __init__(self, base_url: str, access_key: str, secret_key: str, bucket_name: str, region: str = "us-east-1"):
        self.base_url = base_url
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.region = region
        self.DATE_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"
        self.host = base_url.replace("http://", "").replace("https://", "")
        self.client = minio.Minio(self.host, access_key=access_key, secret_key=secret_key)
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

    def _generate_aws_signature_v4(self, method: str, path: str, expiry: int = None) -> Tuple[dict, str]:
        path = f"/{self.bucket_name}{path}"
        service = "s3"

        # Create a timestamp for the request
        t = datetime.utcnow()
        amz_date = t.strftime("%Y%m%dT%H%M%SZ")
        datestamp = t.strftime("%Y%m%d")

        # Create a canonical request
        canonical_uri = path
        canonical_querystring = ""
        if expiry is not None:
            canonical_querystring = f"Expires={expiry}"
        canonical_headers = "host:" + self.host + "\n" + "x-amz-date:" + amz_date + "\n"
        signed_headers = "host;x-amz-date"
        payload_hash = hashlib.sha256("".encode("utf-8")).hexdigest()
        canonical_request = (
            method
            + "\n"
            + canonical_uri
            + "\n"
            + canonical_querystring
            + "\n"
            + canonical_headers
            + "\n"
            + signed_headers
            + "\n"
            + payload_hash
        )

        # Create a string to sign
        algorithm = "AWS4-HMAC-SHA256"
        credential_scope = datestamp + "/" + self.region + "/" + service + "/" + "aws4_request"
        string_to_sign = (
            algorithm
            + "\n"
            + amz_date
            + "\n"
            + credential_scope
            + "\n"
            + hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
        )

        # Create a signing key
        k_date = hmac.new(
            ("AWS4" + self.secret_key).encode("utf-8"), datestamp.encode("utf-8"), hashlib.sha256
        ).digest()
        k_region = hmac.new(k_date, self.region.encode("utf-8"), hashlib.sha256).digest()
        k_service = hmac.new(k_region, service.encode("utf-8"), hashlib.sha256).digest()
        k_signing = hmac.new(k_service, b"aws4_request", hashlib.sha256).digest()

        # Calculate the signature
        signature = hmac.new(k_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

        # Add the signature to the request as an Authorization header
        authorization_header = (
            algorithm
            + " "
            + "Credential="
            + self.access_key
            + "/"
            + credential_scope
            + ", "
            + "SignedHeaders="
            + signed_headers
            + ", "
            + "Signature="
            + signature
        )
        # Send the request with the authorization header
        headers = {"x-amz-date": amz_date, "Authorization": authorization_header}
        request_url = self.base_url + path + "?" + canonical_querystring

        return headers, request_url

    # skipcq: PYL-W0613
    async def upload(self, file: BinaryIO, file_name: str, size: int | None, mime_type: str | None = None) -> None:
        headers, url = self._generate_aws_signature_v4(method="PUT", path=f"/{file_name}")
        file_size = 0
        while True:
            chunk = file.read(1024)
            file_size += len(chunk)
            if not chunk:
                file.seek(0)
                break
        headers["Content-Length"] = str(file_size)

        async with ClientSession() as session, session.put(url, headers=headers, data=file) as resp:
            if resp.status == 200:
                return None
            else:
                print(await resp.text())
                raise SavingFailedError

    async def delete(self, file_names: list[str]) -> None:
        for file in file_names:
            headers, url = self._generate_aws_signature_v4(method="DELETE", path=f"/{file}")
            async with ClientSession() as session, session.delete(url, headers=headers) as resp:
                if resp.status == 204:
                    return None
                else:
                    raise DeletionFailedError

    def get_url(self, expire: int, file_name: str) -> str:
        return self.client.presigned_get_object(
            object_name=file_name, bucket_name=self.bucket_name, expires=timedelta(seconds=expire)
        )

    def size(self, file_name: str) -> int | None:
        try:
            res = self.client.stat_object(bucket_name=self.bucket_name, object_name=file_name)
        except minio.error.S3Error:
            return None
        return res.size

    async def download(self, file_name: str) -> Generator:
        headers, url = self._generate_aws_signature_v4(method="GET", path=f"/{file_name}")

        async with ClientSession() as session, session.get(url, headers=headers) as resp:
            if resp.status == 200:
                async for i in resp.content.iter_chunked(1024):
                    yield i
            elif resp.status == 404:
                yield None
            else:
                raise DownloadingFailedError
        # client = httpx.AsyncClient()
        # async with client.stream("GET", url, headers=headers) as resp:
        #     if resp.status == 200:
        #         yield resp.aiter_bytes()
