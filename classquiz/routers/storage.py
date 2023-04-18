#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

import re

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, RedirectResponse

from classquiz.config import settings, storage
from classquiz.storage.errors import DownloadingFailedError

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
