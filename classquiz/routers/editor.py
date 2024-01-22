# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import asyncio
import uuid
from typing import Optional

import asyncpg.exceptions
import bleach
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from classquiz.config import settings, redis, storage, meilisearch, ALLOWED_TAGS_FOR_QUIZ, arq
from classquiz.db.models import Quiz, QuizInput, User, QuizQuestionType, StorageItem
from classquiz.auth import get_current_user
import os
from datetime import datetime
from uuid import UUID

from classquiz.helpers import get_meili_data, check_image_string, extract_image_ids_from_quiz
from classquiz.storage.errors import DeletionFailedError

settings = settings()

router = APIRouter()

allowed_image_extensions = [".gif", ".jpg", ".jpeg", ".png", ".svg", ".webp", ".jfif"]


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


@router.post("/finish")
async def finish_edit(edit_id: str, quiz_input: QuizInput):
    session_data = await redis.get(f"edit_session:{edit_id}")
    if session_data is None:
        raise HTTPException(status_code=401, detail="Edit ID not found!")
    session_data = EditSessionData.parse_raw(session_data)
    quiz_input.title = bleach.clean(quiz_input.title, tags=ALLOWED_TAGS_FOR_QUIZ, strip=True)
    quiz_input.description = bleach.clean(quiz_input.description, tags=ALLOWED_TAGS_FOR_QUIZ, strip=True)
    if quiz_input.background_color is not None:
        quiz_input.background_color = bleach.clean(quiz_input.background_color, tags=[], strip=True)

    for i, question in enumerate(quiz_input.questions):
        if question.type == QuizQuestionType.ABCD:
            for i2, answer in enumerate(question.answers):
                if answer.color is not None:
                    quiz_input.questions[i].answers[i2].color = bleach.clean(answer.color, tags=[], strip=True)
                if answer.answer == "":
                    quiz_input.questions[i].answers[i2].answer = None
                if answer.answer is not None:
                    quiz_input.questions[i].answers[i2].answer = bleach.clean(
                        answer.answer, tags=ALLOWED_TAGS_FOR_QUIZ, strip=True
                    )

    images_to_delete = []
    old_quiz_data: Quiz = await Quiz.objects.get_or_none(id=session_data.quiz_id, user_id=session_data.user_id)

    for i, question in enumerate(quiz_input.questions):
        image = question.image
        quiz_input.questions[i].question = bleach.clean(
            quiz_input.questions[i].question, tags=ALLOWED_TAGS_FOR_QUIZ, strip=True
        )
        if image == "":
            question.image = None
        if image is not None and not check_image_string(image)[0]:
            raise HTTPException(status_code=400, detail="Image URL(s) aren't valid!")

    if quiz_input.cover_image == "":
        quiz_input.cover_image = None

    if quiz_input.cover_image is not None and not check_image_string(quiz_input.cover_image)[0]:
        raise HTTPException(status_code=400, detail="image url is not valid")

    if quiz_input.background_image is not None and not check_image_string(quiz_input.background_image)[0]:
        raise HTTPException(status_code=400, detail="image url is not valid")

    if session_data.edit:
        await arq.enqueue_job("quiz_update", old_quiz_data, old_quiz_data.id, _defer_by=2)
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
        quiz.background_color = quiz_input.background_color
        quiz.background_image = quiz_input.background_image
        quiz.mod_rating = None
        for image in images_to_delete:
            if image is not None:
                try:
                    await storage.delete([image])
                except DeletionFailedError:
                    pass
        await redis.srem("edit_sessions", edit_id)
        await redis.delete(f"edit_session:{edit_id}")
        await redis.delete(f"edit_session:{edit_id}:images")
        await quiz.update()
        return quiz
    else:
        quiz = Quiz(
            **quiz_input.dict(),
            user_id=session_data.user_id,
            id=session_data.quiz_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        await redis.delete("global_quiz_count")
        if quiz_input.public:
            meilisearch.index(settings.meilisearch_index).add_documents([await get_meili_data(quiz)])
        try:
            await redis.srem("edit_sessions", edit_id)
            await redis.delete(f"edit_session:{edit_id}")
            await redis.delete(f"edit_session:{edit_id}:images")
            await quiz.save()
        except asyncpg.exceptions.UniqueViolationError:
            raise HTTPException(status_code=400, detail="The quiz already exists")
        new_images = extract_image_ids_from_quiz(quiz)
        for image in new_images:
            item = await StorageItem.objects.get_or_none(id=uuid.UUID(image))
            if item is None:
                continue
            await quiz.storageitems.add(item)
