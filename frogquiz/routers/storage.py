# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0
from base64 import b64encode
from datetime import datetime, timedelta
from tempfile import SpooledTemporaryFile

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Request, Response
from fastapi.responses import StreamingResponse, RedirectResponse
from pydantic import BaseModel

from frogquiz.auth import get_current_user, get_current_user_optional
from frogquiz.config import settings, storage, arq, UPLOAD_LIMITS, MAX_UPLOAD_SIZE
from frogquiz.db.models import User, StorageItem, PublicStorageItem, UpdateStorageItem, PrivateStorageItem
from frogquiz.helpers import check_image_string
from frogquiz.storage.errors import DownloadingFailedError
from uuid import uuid4, UUID

settings = settings()

router = APIRouter()


async def release_storage_quota(user: User | None, size: int) -> None:
    """Give a user back the bytes a deleted file was using.

    `storage_used` was only ever incremented -- by the calculate_hash worker job, once
    per upload -- and nothing anywhere decremented it: not this delete endpoint, not the
    quiz-update job that unlinks a replaced image, not account deletion. So the figure
    was a lifetime upload counter, not usage, and the quota built on it was a lifetime
    cap. Swap a cover image enough times and you are locked out for good with no way to
    reclaim anything, which only became reachable once the quota was actually enforced.

    Clamped at zero because the column declares `minimum=0`: a double release on a row
    whose size was never measured (every row predating the size fix stores 0) would
    otherwise raise rather than no-op.
    """
    if user is None or size <= 0:
        return
    fresh = await User.objects.get_or_none(id=user.id)
    if fresh is None:
        return
    fresh.storage_used = max(0, fresh.storage_used - size)
    await fresh.update()


def headers_from_storage_item(item: StorageItem) -> dict[str, str]:
    base_headers = {"Content-Type": item.mime_type}
    if item.hash is not None:
        base_headers["X-Hash"] = item.hash.hex()
    if item.thumbhash is not None:
        base_headers["X-Thumbhash"] = item.thumbhash
    if item.alt_text is not None:
        base_headers["X-Alt-Text"] = b64encode(item.alt_text.encode("utf-8")).decode()
    if item.size != 0:
        base_headers["Content-Size"] = str(item.size)
    return base_headers


@router.get("/download/{file_name}")
async def download_file(file_name: str):
    item = None
    checked_image_string = check_image_string(file_name)
    if not checked_image_string[0]:
        raise HTTPException(status_code=400, detail="Invalid file name")
    if checked_image_string[1] is not None:
        item = await StorageItem.objects.get_or_none(id=checked_image_string[1])
        if item is None:
            print("Item not found")
            raise HTTPException(status_code=404, detail="File not found")
        file_name = item.storage_path
        if file_name is None:
            file_name = item.id.hex
    if storage.backend == "s3":
        if item is None:
            return RedirectResponse(url=await storage.get_url(file_name, 300))
        else:
            return RedirectResponse(url=await storage.get_url(file_name, 300), headers=headers_from_storage_item(item))
    try:
        download = storage.download(file_name)
    except DownloadingFailedError:
        print("error")
        raise HTTPException(status_code=404, detail="File not found")
    if download is None:
        print("dload is none")
        raise HTTPException(status_code=404, detail="File not found")
    media_type = "image/*"
    if item is not None:
        media_type = item.mime_type
    headers = {"Cache-Control": "public, immutable, max-age=31536000"}
    if item is not None:
        headers = {**headers, **headers_from_storage_item(item)}

    return StreamingResponse(
        download,
        media_type=media_type,
        headers=headers,
    )


@router.get("/info/{file_name}")
async def get_basic_file_info(file_name: str) -> Response:
    checked_image_string = check_image_string(file_name)
    if not checked_image_string[0]:
        raise HTTPException(status_code=404, detail="Invalid file name")
    if checked_image_string[1] is not None:
        item = await StorageItem.objects.get_or_none(id=checked_image_string[1])
        if item is None:
            raise HTTPException(status_code=404, detail="File not found")
        # return PublicStorageItem.from_db_model(item)
        storage_file_name = item.storage_path
        if storage_file_name is None:
            storage_file_name = item.id.hex
        resp = Response(status_code=200, headers=headers_from_storage_item(item))
    else:
        resp = Response(status_code=200, headers={"Content-Type": "image/*"})
    return resp


@router.head("/download/{file_name}")
async def download_file_head(file_name: str) -> Response:
    checked_image_string = check_image_string(file_name)
    if not checked_image_string[0]:
        raise HTTPException(status_code=404, detail="Invalid file name")
    if checked_image_string[1] is not None:
        item = await StorageItem.objects.get_or_none(id=checked_image_string[1])
        if item is None:
            raise HTTPException(status_code=404, detail="File not found")
        # return PublicStorageItem.from_db_model(item)
        storage_file_name = item.storage_path
        if storage_file_name is None:
            storage_file_name = item.id.hex
        resp = Response(status_code=200, headers=headers_from_storage_item(item))
    else:
        resp = Response(status_code=200, headers={"Content-Type": "image/*"})
        storage_file_name = file_name
    if storage.backend == "s3":
        resp.status_code = 307
        resp.headers.append("Location", await storage.get_url(storage_file_name, 300))
    return resp


class UploadLimits(BaseModel):
    """What the editor's file picker is allowed to offer."""

    # mime type -> largest file in bytes
    per_type: dict[str, int]
    # The smallest of those, which is the number to show a person: the picker does not
    # know which type they are about to choose.
    max_file_size: int
    accepted_types: list[str]


@router.get("/limits")
async def get_upload_limits() -> UploadLimits:
    """The upload rules, so the browser does not carry its own copy of them.

    The editor used to hardcode a 10MB cap and its own list of four mime types in
    `uploader.svelte`, neither of which matched the server. Reading them means a
    change to `config.py` moves both.
    """
    return UploadLimits(
        per_type=UPLOAD_LIMITS,
        max_file_size=min(UPLOAD_LIMITS.values()),
        accepted_types=list(UPLOAD_LIMITS),
    )


@router.post("/")
async def upload_file(
    file: UploadFile = File(), user: User | None = Depends(get_current_user_optional)
) -> PublicStorageItem:
    # Cover/background/question images are uploaded from the quiz editor, which an
    # anonymous host can use end to end (see routers/editor.py). Requiring a login
    # here made every upload from that flow fail silently in the UI -- there is no
    # per-user quota to check without a user, so anonymous uploads skip it.
    limit = UPLOAD_LIMITS.get(file.content_type)
    if limit is None:
        raise HTTPException(status_code=422, detail="Unsupported")
    # The size, before anything is written. This route used to pass size=0 into storage
    # and store 0 on the row, so nothing in the request path ever knew how big the file
    # was: the only cap in the product was Uppy's, in the browser, and this endpoint
    # takes anonymous uploads. `request_size_guard` in frogquiz/__init__.py rejects on
    # Content-Length before the body is read; this is the check that cannot be lied to,
    # because by now the bytes are counted.
    #
    # Starlette fills .size from the multipart parser. It is None only if the part
    # carried no length, in which case fall back to measuring the spooled file.
    file_size = file.size
    if file_size is None:
        file_size = file.file.seek(0, 2)
        file.file.seek(0)
    if file_size > limit:
        raise HTTPException(
            status_code=413,
            detail=f"File is too large: {file_size} bytes, limit is {limit}",
        )
    if file_size == 0:
        raise HTTPException(status_code=422, detail="File is empty")
    # Checked against the file in hand, not just the account's running total, so the
    # last upload before the quota cannot be an arbitrarily large one. The total is
    # maintained by the calculate_hash worker job.
    if user is not None and user.storage_used + file_size > settings.free_storage_limit:
        raise HTTPException(status_code=409, detail="Storage limit reached")
    file_id = uuid4()
    file_obj = StorageItem(
        id=file_id,
        uploaded_at=datetime.now(),
        mime_type=file.content_type,
        hash=None,
        user=user,
        size=file_size,
        deleted_at=None,
        alt_text=None,
    )
    await storage.upload(
        file_name=file_id.hex,
        file_data=file.file,
        mime_type=file.content_type,
        size=file_size,
    )
    await file_obj.save()
    await arq.enqueue_job("calculate_hash", file_id.hex)
    return PublicStorageItem.from_db_model(file_obj)


@router.post("/raw")
async def upload_raw_file(request: Request, user: User = Depends(get_current_user)) -> PublicStorageItem:
    if user.storage_used > settings.free_storage_limit:
        raise HTTPException(status_code=409, detail="Storage limit reached")
    mime_type = request.headers.get("Content-Type")
    limit = UPLOAD_LIMITS.get(mime_type)
    if limit is None:
        raise HTTPException(status_code=422, detail="Unsupported")
    file_id = uuid4()
    data_file = SpooledTemporaryFile(max_size=1000)
    # This one reads the body itself, so unlike the multipart route it can stop in the
    # middle of a transfer rather than measuring the whole thing after the fact. It
    # stored size=0 and had no cap at all, which on the S3 backend means the payload
    # is then read into memory in one piece to be signed.
    file_size = 0
    async for chunk in request.stream():
        file_size += len(chunk)
        if file_size > limit:
            data_file.close()
            raise HTTPException(status_code=413, detail=f"File is too large: limit is {limit} bytes")
        data_file.write(chunk)
    if file_size == 0:
        data_file.close()
        raise HTTPException(status_code=422, detail="File is empty")
    if user.storage_used + file_size > settings.free_storage_limit:
        data_file.close()
        raise HTTPException(status_code=409, detail="Storage limit reached")
    data_file.seek(0)
    file_obj = StorageItem(
        id=file_id,
        uploaded_at=datetime.now(),
        mime_type=mime_type,
        hash=None,
        user=user,
        size=file_size,
        deleted_at=None,
        alt_text=None,
    )
    # https://github.com/VirusTotal/vt-py/issues/119#issuecomment-1261246867
    await storage.upload(
        file_name=file_id.hex,
        # skipcq: PYL-W0212
        file_data=data_file._file,
        mime_type=mime_type,
        size=file_size,
    )
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
    await release_storage_quota(user, file_data.size)
    return


@router.put("/meta/{file_id}")
async def update_image_data(
    file_id: UUID, data: UpdateStorageItem, user: User = Depends(get_current_user)
) -> PublicStorageItem:
    file_data = await StorageItem.objects.get_or_none(id=file_id, user=user, deleted_at=None)
    if file_data is None:
        raise HTTPException(status_code=404, detail="File not found")
    if data.alt_text == "":
        data.alt_text = None
    if data.filename == "":
        data.filename = None
    file_data.filename = data.filename
    file_data.alt_text = data.alt_text
    await file_data.update()
    return PublicStorageItem.from_db_model(file_data)


@router.get("/list")
async def list_images(
    since: datetime | None = None, user: User = Depends(get_current_user)
) -> list[PrivateStorageItem]:
    if since is None:
        since = datetime.now() - timedelta(weeks=9999)
    storage_items = (
        await StorageItem.objects.filter(user=user)
        .filter(StorageItem.uploaded_at > since)
        .filter(StorageItem.deleted_at == None)  # noqa: E711
        .order_by(StorageItem.uploaded_at.desc())
        .select_related([StorageItem.quizzes, StorageItem.quiztivities])
        .all()
    )
    if len(storage_items) == 0:
        raise HTTPException(status_code=404, detail="No items found")
    return_items: list[PrivateStorageItem] = []
    for item in storage_items:
        return_items.append(PrivateStorageItem.from_db_model(item))
    return return_items


@router.get("/list/last")
async def get_latest_images(count: int = 50, user: User = Depends(get_current_user)) -> list[PrivateStorageItem]:
    count = min(count, 50)
    items = (
        await StorageItem.objects.filter(user=user)
        .limit(count)
        .select_related([StorageItem.quizzes, StorageItem.quiztivities])
        .order_by(StorageItem.uploaded_at.desc())
        .all()
    )
    return_items: list[PrivateStorageItem] = []
    for item in items:
        return_items.append(PrivateStorageItem.from_db_model(item))
    return return_items


class ReturnGetStorageLimit(BaseModel):
    limit: int
    limit_reached: bool
    used: int


@router.get("/limit")
async def get_storage_limit(user: User = Depends(get_current_user)) -> ReturnGetStorageLimit:
    user = await User.objects.get_or_none(id=user.id)
    if user.storage_used > settings.free_storage_limit:
        return ReturnGetStorageLimit(limit=settings.free_storage_limit, limit_reached=True, used=user.storage_used)
    else:
        return ReturnGetStorageLimit(limit=settings.free_storage_limit, limit_reached=False, used=user.storage_used)
