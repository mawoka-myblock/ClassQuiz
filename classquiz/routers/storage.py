#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
from datetime import datetime

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import StreamingResponse, RedirectResponse

from classquiz.auth import get_current_user
from classquiz.config import settings, storage, arq
from classquiz.db.models import User, StorageItem, PublicStorageItem, UpdateStorageItem
from classquiz.helpers import check_image_string
from classquiz.storage.errors import DownloadingFailedError
from uuid import uuid4, UUID

settings = settings()

router = APIRouter()

file_regex = r"^[a-z0-9]{8}-[a-z0-9-]{27}--[a-z0-9-]{36}$"


@router.get("/download/{file_name}")
async def download_file(file_name: str):
    checked_image_string = check_image_string(file_name)
    if not checked_image_string[0]:
        raise HTTPException(status_code=400, detail="Invalid file name")
    if checked_image_string[1] is not None:
        item = await StorageItem.objects.get_or_none(id=checked_image_string[1])
        if item is None:
            raise HTTPException(status_code=404, detail="File not found")
        file_name = item.storage_path
        if file_name is None:
            file_name = item.id.hex
    if storage.backend == "s3":
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
async def upload_file(file: UploadFile = File(), user: User = Depends(get_current_user)) -> PublicStorageItem:
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
    return PublicStorageItem.from_db_model(file_obj)


@router.get("/meta/{file_id}")
async def get_file_info(file_id: UUID, user: User = Depends(get_current_user)) -> PublicStorageItem:
    file_data = await StorageItem.objects.get_or_none(id=file_id, user=user, deleted_at=None)
    if file_data is None:
        raise HTTPException(status_code=404, detail="File not found")
    return PublicStorageItem.from_db_model(file_data)


@router.delete("/meta/{file_id}")
async def mark_file_as_deleted(file_id: UUID, user: User = Depends(get_current_user)):
    file_data = await StorageItem.objects.get_or_none(id=file_id, user=user, deleted_at=None)
    if file_data is None:
        raise HTTPException(status_code=404, detail="File not found")
    storage_path = file_data.storage_path
    if storage_path is None:
        storage_path = file_data.id.hex
    await storage.delete(storage_path)
    file_data.deleted_at = datetime.now()
    await file_data.update()
    return


@router.put("/meta/{file_id}")
async def update_image_data(
    file_id: UUID, data: UpdateStorageItem, user: User = Depends(get_current_user)
) -> PublicStorageItem:
    file_data = await StorageItem.objects.get_or_none(id=file_id, user=user, deleted_at=None)
    if file_data is None:
        raise HTTPException(status_code=404, detail="File not found")
    file_data.filename = data.filename
    file_data.alt_text = data.alt_text
    await file_data.update()
    return PublicStorageItem.from_db_model(file_data)
