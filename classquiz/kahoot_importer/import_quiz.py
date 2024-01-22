# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import io
import json
import uuid
from datetime import datetime

import bleach
from aiohttp import ClientSession

from classquiz.config import settings, storage, meilisearch, ALLOWED_TAGS_FOR_QUIZ, arq
from classquiz.db.models import Quiz, ABCDQuizAnswer, QuizQuestion, User, StorageItem
from classquiz.kahoot_importer.get import get as get_quiz
from classquiz.helpers import get_meili_data

settings = settings()


async def _download_image(url: str) -> bytes:
    async with ClientSession() as session, session.get(url) as resp:
        return await resp.read()


DEFAULT_COLORS = ["#D6EDC9", "#B07156", "#7F7057", "#4E6E58"]


async def handle_image_upload(url: str, user: User) -> StorageItem:
    image_bytes = await _download_image(url)
    file_obj = StorageItem(
        id=uuid.uuid4(),
        uploaded_at=datetime.now(),
        mime_type="application/octet-stream",
        hash=None,
        user=user,
        size=0,
        deleted_at=None,
        alt_text=None,
        imported=True,
    )
    await file_obj.save()
    await storage.upload(file_name=file_obj.id.hex, file_data=io.BytesIO(image_bytes))
    await arq.enqueue_job("calculate_hash", file_obj.id.hex)
    return file_obj


async def import_quiz(quiz_id: str, user: User) -> Quiz | int:
    """
    Imports a quiz from Kahoot.
    :param user: The user object
    :param quiz_id: The ID of the quiz to import.
    :return: True if the import was successful, False otherwise.
    """
    kahoot_quiz_id = quiz_id
    quiz = await get_quiz(kahoot_quiz_id)
    if type(quiz) is int:
        return quiz
    quiz_questions: list[dict] = []
    quiz_id = uuid.uuid4()
    meilisearch.delete_index(settings.meilisearch_index)
    meilisearch.create_index(settings.meilisearch_index)
    uploaded_images: list[StorageItem] = []

    for q in quiz.kahoot.questions:
        answers: list[ABCDQuizAnswer] = []
        image = None
        if q.image is not None and q.image != "":
            image_obj = await handle_image_upload(q.image, user)
            uploaded_images.append(image_obj)
            image = image_obj.id.hex
        for i, a in enumerate(q.choices):
            answers.append(
                (
                    ABCDQuizAnswer(
                        right=a.correct,
                        answer=bleach.clean(a.answer, tags=[], strip=True),
                        color=DEFAULT_COLORS[i],
                    )
                )
            )

        quiz_questions.append(
            QuizQuestion(
                question=bleach.clean(q.question, tags=ALLOWED_TAGS_FOR_QUIZ, strip=True),
                answers=answers,
                time=str(q.time / 1000),
                image=image,
            ).dict()
        )
    cover = None
    if quiz.kahoot.cover != "" and quiz.kahoot.cover is not None:
        img_obj = await handle_image_upload(quiz.kahoot.cover, user)
        uploaded_images.append(img_obj)
        cover = img_obj.id.hex
    quiz_data = Quiz(
        id=quiz_id,
        public=False,
        title=bleach.clean(quiz.kahoot.title, tags=ALLOWED_TAGS_FOR_QUIZ, strip=True),
        description=bleach.clean(quiz.kahoot.description, tags=ALLOWED_TAGS_FOR_QUIZ, strip=True),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        user_id=user.id,
        questions=json.dumps(quiz_questions),
        imported_from_kahoot=True,
        cover_image=cover,
        kahoot_id=uuid.UUID(kahoot_quiz_id),
    )
    meilisearch.index(settings.meilisearch_index).add_documents([await get_meili_data(quiz_data)])
    await quiz_data.save()
    for img in uploaded_images:
        await quiz_data.storageitems.add(img)
    return quiz_data
