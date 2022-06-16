import asyncio
import html
import uuid
from typing import Optional

import bleach
import pydantic
from fastapi import APIRouter, File, Form, UploadFile, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel

from classquiz.config import settings, redis, storage, meilisearch
from classquiz.db.models import Quiz, QuizInput, User
from classquiz.auth import get_current_user
import os
from datetime import datetime
from uuid import UUID

from classquiz.helpers import get_meili_data

router = APIRouter()


class InitEditorResponse(BaseModel):
    token: str


class EditSessionData(BaseModel):
    quiz_id: UUID
    edit: bool
    user_id: UUID


async def delete_images_for_edit_id(edit_id: str):
    await asyncio.sleep(30)
    res = await redis.lrange(f"edit_session:{edit_id}:images", 0, -1)
    if len(res) != 0:
        for image_id in res:
            await storage.delete(image_id)


@router.post("/start", response_model=InitEditorResponse)
async def init_editor(edit: bool, quiz_id: Optional[UUID] = None, user: User = Depends(get_current_user)):
    if edit and quiz_id is not None:
        if await Quiz.objects.get_or_none(id=quiz_id, user_id=user.id) is None:
            raise HTTPException(status_code=404, detail="Quiz not found")
    if not edit and quiz_id is not None:
        raise HTTPException(status_code=400, detail="You can't choose the id for your quiz")
    if edit and quiz_id is None:
        raise HTTPException(status_code=400, detail="Edit can't be true if quiz_id is None")
    if quiz_id is None:
        quiz_id = uuid.uuid4()
    edit_id = os.urandom(4).hex()
    await redis.sadd("edit_sessions", edit_id)
    await redis.set(
        f"edit_session:{edit_id}", EditSessionData(quiz_id=quiz_id, edit=edit, user_id=user.id).json(), ex=3600
    )
    return InitEditorResponse(token=edit_id)


class UploadImageReturn(BaseModel):
    id: str


@router.post("/image", response_model=UploadImageReturn)
async def upload_image(edit_id: str, file: UploadFile = File()):
    session_data = await redis.get(f"edit_session:{edit_id}")
    if session_data is None:
        raise HTTPException(status_code=401, detail="Edit ID not found!")
    session_data = EditSessionData.parse_raw(session_data)
    file_name = f"{session_data.quiz_id}--{uuid.uuid4()}"
    print("Uploading...")
    await storage.upload(file_name=file_name, file_data=await file.read())
    print("Finished Upload")
    await redis.lpush(f"edit_session:{edit_id}:images", file_name)
    return UploadImageReturn(id=file_name)


@router.post("/finish")
async def finish_edit(edit_id: str, quiz_input: QuizInput):
    session_data = await redis.get(f"edit_session:{edit_id}")
    if session_data is None:
        raise HTTPException(status_code=401, detail="Edit ID not found!")
    session_data = EditSessionData.parse_raw(session_data)
    quiz_input.title = html.unescape(bleach.clean(quiz_input.title, tags=[], strip=True))
    quiz_input.description = html.unescape(bleach.clean(quiz_input.description, tags=[], strip=True))
    if session_data.edit:
        quiz = await Quiz.objects.get_or_none(id=session_data.quiz_id, user_id=session_data.user_id)
        meilisearch.index(settings.meilisearch_index).update_documents([await get_meili_data(quiz)])
        if quiz.public and not quiz_input.public:
            meilisearch.index(settings.meilisearch_index).delete_document(str(quiz.id))
        if not quiz.public and quiz_input.public:
            meilisearch.index(settings.meilisearch_index).add_documents([await get_meili_data(quiz)])
        quiz.title = quiz_input.title
        quiz.public = quiz_input.public
        quiz.description = quiz_input.description
        quiz.updated_at = datetime.now()
        quiz.questions = quiz_input.dict()["questions"]
        return await quiz.save()
    else:
        quiz = Quiz(**quiz_input.dict(), user_id=session_data.user_id, id=session_data.quiz_id)
        await redis.delete("global_quiz_count")
        if quiz_input.public:
            meilisearch.index(settings.meilisearch_index).add_documents([await get_meili_data(quiz)])
        return await quiz.save()
