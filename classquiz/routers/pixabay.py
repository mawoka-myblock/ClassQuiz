# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


from datetime import datetime
from io import BytesIO
from uuid import uuid4

from aiohttp import ClientSession
from fastapi import APIRouter, Depends, HTTPException

from classquiz.auth import get_current_user
from classquiz.db.models import User, StorageItem, PublicStorageItem
from classquiz.helpers.pixabay import get_images, GetImagesParams, BoolInput, GetImagesResponse, NotFoundError
from classquiz.config import settings, storage, arq

settings = settings()
router = APIRouter()


@router.get("/images")
async def search_pixabay_images(query: str, page: int = 1, user: User = Depends(get_current_user)) -> GetImagesResponse:
    if settings.pixabay_api_key is None:
        raise HTTPException(status_code=423, detail="Pixabay not set up")
    return await get_images(settings.pixabay_api_key, GetImagesParams(q=query, safesearch=BoolInput.true, page=page))


@router.post("/save")
async def save_pixabay_image(id: str, user: User = Depends(get_current_user)) -> PublicStorageItem:
    if settings.pixabay_api_key is None:
        raise HTTPException(status_code=423, detail="Pixabay not set up")
    if user.storage_used > settings.free_storage_limit:
        raise HTTPException(status_code=409, detail="Storage limit reached")
    try:
        images = await get_images(settings.pixabay_api_key, GetImagesParams(id=id, safesearch=BoolInput.true))
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Pixabay file not found")
    image = images.hits[0]
    file_id = uuid4()
    file_data = b""
    async with ClientSession() as session, session.get(image.largeImageURL) as resp:
        async for i in resp.content.iter_chunked(1024):
            file_data += i
        content_type = resp.headers.get("Content-Type")

    if content_type is None:
        content_type = "image/*"
    file = BytesIO(file_data)
    await storage.upload(file_name=file_id.hex, file_data=file, mime_type=content_type)
    file_obj: StorageItem = StorageItem(
        id=file_id,
        uploaded_at=datetime.now(),
        mime_type=content_type,
        hash=None,
        user=user,
        size=0,
        deleted_at=None,
        alt_text=None,
        imported=True,
    )
    await file_obj.save()
    await arq.enqueue_job("calculate_hash", file_id.hex)
    return PublicStorageItem.from_db_model(file_obj)
