#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import re
from datetime import datetime

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import StreamingResponse, RedirectResponse

from classquiz.auth import get_current_user
from classquiz.config import settings, storage, arq
from classquiz.db.models import User, StorageItem
from classquiz.storage.errors import DownloadingFailedError
from uuid import uuid4

settings = settings()

router = APIRouter()

file_regex = r"^[a-z0-9]{8}-[a-z0-9-]{27}--[a-z0-9-]{36}$"


@router.get("/download/{file_name}")
async def download_file(file_name: str):
    if not re.match(file_regex, file_name):
        raise HTTPException(status_code=400, detail="Invalid file name")
    if storage.backend == "s3":
        print("redir")
        return RedirectResponse(url=await storage.get_url(file_name, 300))
    try:
        download = await storage.download(file_name)
    except DownloadingFailedError:
        raise HTTPException(status_code=404, detail="File not found")
    if download is None:
        raise HTTPException(status_code=404, detail="File not found")

    def iter_file():
        yield from download

    return StreamingResponse(
        iter_file(),
        media_type="image/*",
        headers={"Cache-Control": "public, immutable, max-age=31536000"},
    )


@router.post("/")
async def upload_file(file: UploadFile = File(), user: User = Depends(get_current_user)):
    file_id = uuid4()

    size = 0
    # if file.file.name is None:
    #     size = len(await file.read())
    #     print("MemorySize", size)
    # else:
    #     f = file.file
    #     a = file.file.fileno()
    #     os.path.getsize(file.file.name)
    #     print("DiskSize", size, "name:", file.file.name, "a:", file.file.tell(), "size")
    file_obj = StorageItem(
        id=file_id,
        uploaded_at=datetime.now(),
        mime_type=file.content_type,
        hash=None,
        user=user,
        size=size,
        deleted_at=None,
        alt_text=None,
    )
    file_data = await file.read()
    await storage.upload(file_name=file_id.hex, file_data=file_data)
    await file_obj.save()
    await arq.enqueue_job("calculate_hash", file_id.hex)
