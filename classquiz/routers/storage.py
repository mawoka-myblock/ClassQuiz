from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from classquiz.config import settings
import re
from classquiz.storage import Storage

settings = settings()

router = APIRouter()

file_regex = r"^[a-z0-9]{8}-[a-z0-9-]{27}--[a-z0-9-]{36}$"


@router.get('/download/{file_name}')
async def download_file(file_name: str):
    storage = Storage(backend=settings.storage_backend, deta_key=settings.deta_project_key,
                      deta_id=settings.deta_project_id, storage_path=settings.storage_path)
    if not re.match(file_regex, file_name):
        raise HTTPException(status_code=400, detail="Invalid file name")

    download = await storage.download(file_name)
    if download is None:
        raise HTTPException(status_code=404, detail="File not found")

    def iter_file():
        yield from download

    return StreamingResponse(iter_file(), media_type='image/*',
                             headers={"Cache-Control": "public, immutable, max-age=31536000"})
