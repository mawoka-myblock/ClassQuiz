#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

import asyncio
import html
import re
import uuid
from typing import Optional

import asyncpg.exceptions
import bleach
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from pydantic import BaseModel

from classquiz.config import settings, redis, storage, meilisearch
from classquiz.db.models import Quiz, QuizInput, User
import puremagic
from classquiz.auth import get_current_user
import os
from datetime import datetime
from uuid import UUID

from classquiz.helpers import get_meili_data, check_hashcash
from classquiz.storage.errors import DeletionFailedError

settings = settings()

router = APIRouter()

allowed_image_extensions = [".gif", ".jpg", ".jpeg", ".png", ".svg", ".webp"]


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
            await storage.delete([image_id])


@router.post("/start", response_model=InitEditorResponse)
async def init_editor(edit: bool, quiz_id: Optional[UUID] = None, user: User = Depends(get_current_user)):
    if edit and quiz_id is not None and await Quiz.objects.get_or_none(id=quiz_id, user_id=user.id) is None:
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


class GetPowData(BaseModel):
    data: str


@router.get("/pow", response_model=GetPowData)
async def get_pow_data(edit_id: str):
    session_data = await redis.get(f"edit_session:{edit_id}")
    if session_data is None:
        raise HTTPException(status_code=401, detail="Edit ID not found!")
    random_str = os.urandom(8).hex()
    await redis.set(f"edit_session:{edit_id}:pow", random_str, ex=3800)
    return GetPowData(data=random_str)


class UploadImageReturn(BaseModel):
    id: str
    pow_data: str


@router.post("/image", response_model=UploadImageReturn)
async def upload_image(edit_id: str, pow_data: str, file: UploadFile = File()):
    session_data = await redis.get(f"edit_session:{edit_id}")
    pow_data_server = await redis.get(f"edit_session:{edit_id}:pow")
    uploaded_images = await redis.llen(f"edit_session:{edit_id}:images")
    if pow_data_server is None:
        raise HTTPException(status_code=401, detail="Edit ID not found!")
    if session_data is None:
        raise HTTPException(status_code=401, detail="Edit ID not found!")

    if uploaded_images == 0 and not check_hashcash(pow_data, pow_data_server, "8"):
        raise HTTPException(status_code=401, detail="Edit ID not found!")
    if uploaded_images != 0 and not check_hashcash(pow_data, pow_data_server, "8"):
        raise HTTPException(status_code=401, detail="Edit ID not found!")
    file_bytes = await file.read()
    if len(file_bytes) < 2000:
        raise HTTPException(status_code=400, detail="File too large")
    pm_data = puremagic.magic_string(file_bytes)[0]
    if pm_data.extension not in allowed_image_extensions:
        raise HTTPException(status_code=400, detail="Image-type now allowed!")
    session_data = EditSessionData.parse_raw(session_data)
    file_name = f"{session_data.quiz_id}--{uuid.uuid4()}"
    await storage.upload(file_name=file_name, file_data=file_bytes)
    await redis.lpush(f"edit_session:{edit_id}:images", file_name)
    random_str = os.urandom(8).hex()
    await redis.set(f"edit_session:{edit_id}:pow", random_str, ex=3800)
    return UploadImageReturn(id=file_name, pow_data=random_str)


@router.post("/finish")
async def finish_edit(edit_id: str, quiz_input: QuizInput):
    session_data = await redis.get(f"edit_session:{edit_id}")
    if session_data is None:
        raise HTTPException(status_code=401, detail="Edit ID not found!")
    session_data = EditSessionData.parse_raw(session_data)
    quiz_input.title = html.unescape(bleach.clean(quiz_input.title, tags=[], strip=True))
    quiz_input.description = html.unescape(bleach.clean(quiz_input.description, tags=[], strip=True))
    image_id_regex = r"^.{36}--.{36}$"
    imgur_regex = r"^https://i\.imgur\.com\/.{7}.(jpg|png|gif)$"
    server_regex = rf"^{re.escape(settings.root_address)}/api/v1/storage/download/.{{36}}--.{{36}}$"
    extract_file_name_re = r"^.*/api/v1/storage/download/(.{36}--.{36})$"
    images_to_delete = []
    old_quiz_data = await Quiz.objects.get_or_none(id=session_data.quiz_id, user_id=session_data.user_id)

    def mark_image_for_deletion(new: str | None, index: int, old_quiz: Quiz | None):
        if old_quiz is None:
            return
        try:
            if new == old_quiz.questions[index]["image"]:
                return
            else:
                images_to_delete.append(old_quiz.questions[index]["image"])
        except IndexError:
            pass

    for i, question in enumerate(quiz_input.questions):
        image = question.image
        if image == "":
            question.image = None
            mark_image_for_deletion(question.image, i, old_quiz_data)
        elif image is None:
            mark_image_for_deletion(question.image, i, old_quiz_data)
        elif bool(re.match(image_id_regex, question.image)):
            question.image = f"{settings.root_address}/api/v1/storage/download/{image}"
            mark_image_for_deletion(question.image, i, old_quiz_data)
        elif bool(re.match(imgur_regex, image)):
            mark_image_for_deletion(question.image, i, old_quiz_data)
        elif bool(re.match(server_regex, image)):
            mark_image_for_deletion(question.image, i, old_quiz_data)
        else:
            raise HTTPException(status_code=400, detail="Image URL(s) aren't valid!")

    if quiz_input.cover_image == "":
        quiz_input.cover_image = None

    if quiz_input.cover_image is not None and not bool(re.match(server_regex, quiz_input.cover_image)):
        raise HTTPException(status_code=400, detail="image url is not valid")

    if session_data.edit:
        quiz = old_quiz_data
        meilisearch.index(settings.meilisearch_index).update_documents([await get_meili_data(quiz)])
        if not quiz_input.public:
            meilisearch.index(settings.meilisearch_index).delete_document(str(quiz.id))
        else:
            meilisearch.index(settings.meilisearch_index).add_documents([await get_meili_data(quiz)])
        quiz.title = quiz_input.title
        quiz.public = quiz_input.public
        quiz.description = quiz_input.description
        quiz.updated_at = datetime.now()
        quiz.questions = quiz_input.dict()["questions"]
        quiz.cover_image = quiz_input.cover_image
        for image in images_to_delete:
            if image is not None:
                try:
                    await storage.delete([re.search(extract_file_name_re, image).group(1)])
                except DeletionFailedError:
                    pass
        await redis.srem("edit_sessions", edit_id)
        await redis.delete(f"edit_session:{edit_id}")
        await redis.delete(f"edit_session:{edit_id}:images")
        return await quiz.update()
    else:
        quiz = Quiz(**quiz_input.dict(), user_id=session_data.user_id, id=session_data.quiz_id)
        await redis.delete("global_quiz_count")
        if quiz_input.public:
            meilisearch.index(settings.meilisearch_index).add_documents([await get_meili_data(quiz)])
        try:
            await redis.srem("edit_sessions", edit_id)
            await redis.delete(f"edit_session:{edit_id}")
            await redis.delete(f"edit_session:{edit_id}:images")
            return await quiz.save()
        except asyncpg.exceptions.UniqueViolationError:
            raise HTTPException(status_code=400, detail="The quiz already exists")
