#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

import pytest

from classquiz.config import settings
from classquiz.storage import Storage

settings = settings()

file_contents = b"hello world"


def test_storage_init():
    with pytest.raises(NotImplementedError):
        Storage(
            backend="asdsad",
            deta_key=settings.deta_project_key,
            deta_id=settings.deta_project_id,
            storage_path=settings.storage_path,
        )
    with pytest.raises(ValueError):
        Storage(backend="deta", deta_key=None, deta_id=None, storage_path=None)
    with pytest.raises(ValueError):
        Storage(backend="local", storage_path=None, deta_key=None, deta_id=None)


async def storage_tester(storage: Storage):
    res = await storage.upload(file_name="test.txt", file_data=file_contents)
    assert res is None
    res = await storage.download(file_name="test.txt")
    assert res.read() == file_contents
    res = await storage.delete(file_names=["test.txt"])
    assert res is None
    res = await storage.download(file_name="test.txt")
    assert res is None
    res = await storage.delete(file_names=["test.txt"])
    assert res is None


@pytest.mark.asyncio
async def test_deta():
    storage: Storage = Storage(
        backend="deta",
        deta_key=settings.deta_project_key,
        deta_id=settings.deta_project_id,
        storage_path=settings.storage_path,
    )
    await storage_tester(storage)


@pytest.mark.asyncio
async def test_local():
    storage: Storage = Storage(backend="local", storage_path=settings.storage_path, deta_key=None, deta_id=None)
    await storage_tester(storage)


@pytest.mark.asyncio
async def test_minio():
    storage: Storage = Storage(
        backend="s3",
        access_key="Q3AM3UQ867SPQQA43P2F",
        secret_key="zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG",
        bucket_name="classquiz",
        base_url="https://play.min.io",
        deta_key=None,
        deta_id=None,
        storage_path=None,
    )
    await storage_tester(storage)
    await storage.upload(file_name="test.txt", file_data=file_contents)
    url = await storage.get_url(file_name="test.txt", expiry=20)
    assert url is not None
