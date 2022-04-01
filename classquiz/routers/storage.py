from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from classquiz.config import settings
import io
from classquiz.storage import Storage

settings = settings()

router = APIRouter()


@router.get('/download/{file_name}')
async def download_file(file_name: str):
    storage = Storage(backend=settings.storage_backend, deta_key=settings.deta_project_key,
                      deta_id=settings.deta_project_id)
    download = await storage.download(file_name)

    def iter_file():
        yield from download

    return StreamingResponse(iter_file(), media_type='image/*',
                             headers={"Cache-Control": "public, immutable, max-age=31536000"})
