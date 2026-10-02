# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import io

import pytest

from frogquiz.config import settings
from frogquiz.storage import Storage

settings = settings()

file_contents = b"hello world"


def test_storage_init():
    with pytest.raises(NotImplementedError):
        Storage(
            backend="asdsad",
            storage_path=settings.storage_path,
        )
    with pytest.raises(ValueError):
        Storage(backend="s3", base_url=None, secret_key=None, access_key=None, storage_path=None)
    with pytest.raises(ValueError):
        Storage(backend="local", storage_path=None)


async def storage_tester(storage: Storage):
    res = await storage.upload(file_name="test.txt", file_data=io.BytesIO(initial_bytes=file_contents))
    assert res is None
    res = storage.download(file_name="test.txt")
    async for chunk in res:
        assert bytes(chunk) == file_contents
    res = await storage.get_file_size(file_name="test.txt")
    assert res == len(file_contents)
    res = await storage.get_file_size(file_name="asdsadasdasdadfdsf.txt")
    assert res is None
    res = await storage.delete(file_names=["test.txt"])
    assert res is None
    res = storage.download(file_name="test.txt")
    async for chunk in res:
        assert chunk is None
    res = await storage.delete(file_names=["test.txt"])
    assert res is None


@pytest.mark.asyncio
async def test_local():
    storage: Storage = Storage(backend="local", storage_path=settings.storage_path)
    await storage_tester(storage)


@pytest.mark.asyncio
async def test_local_creates_its_directory(tmp_path):
    """A STORAGE_PATH that does not exist yet is created, not a 500 on first upload.

    `LocalStorage.upload` is a bare open(..., "wb"), so without this every upload failed
    with FileNotFoundError and nothing in the response said why. Docker masked it (the
    bind mount makes the path); a bare-VM install or a fresh test box did not.
    """
    missing = tmp_path / "not" / "there" / "yet"
    assert not missing.exists()
    storage: Storage = Storage(backend="local", storage_path=str(missing))
    assert missing.is_dir()
    # And it is usable, not merely present.
    await storage_tester(storage)


@pytest.mark.skip(
    reason=(
        "Depends on play.min.io, a public MinIO demo server this suite does not "
        "control and has no local stand-in for. It has gone unreachable from "
        "GitHub's own runners for stretches at a time (ConnectTimeoutError, not a "
        "test failure), which blocks CI on nothing this repo can fix. Re-enable "
        "once there's a real S3-compatible target to test against -- a MinIO "
        "service in docker-compose.dev.yml alongside db/redis/meilisearch, per "
        "run_tests.sh, would be the natural replacement."
    )
)
@pytest.mark.asyncio
async def test_minio():
    storage: Storage = Storage(
        backend="s3",
        access_key="Q3AM3UQ867SPQQA43P2F",
        secret_key="zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG",
        bucket_name="frogquiz",
        base_url="https://play.min.io",
        storage_path=None,
    )
    await storage_tester(storage)
    await storage.upload(file_name="test.txt", file_data=io.BytesIO(initial_bytes=file_contents))
    url = await storage.get_url(file_name="test.txt", expiry=20)
    assert url is not None
