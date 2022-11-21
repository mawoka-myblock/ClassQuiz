#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

import html
import json
import uuid
from datetime import datetime

import bleach
from aiohttp import ClientSession

from classquiz.config import settings, storage, meilisearch, ALLOWED_TAGS_FOR_QUIZ
from classquiz.db.models import Quiz, ABCDQuizAnswer, QuizQuestion, User
from classquiz.kahoot_importer.get import get as get_quiz
from classquiz.helpers import get_meili_data

settings = settings()


async def _download_image(url: str) -> bytes:
    async with ClientSession() as session, session.get(url) as resp:
        return await resp.read()


async def import_quiz(quiz_id: str, user: User) -> Quiz | str:
    """
    Imports a quiz from Kahoot.
    :param user: The user object
    :param quiz_id: The ID of the quiz to import.
    :return: True if the import was successful, False otherwise.
    """
    quiz = await get_quiz(quiz_id)
    if quiz is None:
        return "quiz not found"
    quiz_questions: list[dict] = []
    quiz_id = uuid.uuid4()
    meilisearch.delete_index(settings.meilisearch_index)
    meilisearch.create_index(settings.meilisearch_index)

    for q in quiz.kahoot.questions:
        answers: list[ABCDQuizAnswer] = []
        image = None
        if q.image is not None and q.image != "":
            image_bytes = await _download_image(q.image)
            image_name = f"{quiz_id}--{uuid.uuid4()}"
            image = await storage.upload(file_name=image_name, file_data=image_bytes)
            image = f"{settings.root_address}/api/v1/storage/download/{image_name}"
        for a in q.choices:
            answers.append(
                (ABCDQuizAnswer(right=a.correct, answer=html.unescape(bleach.clean(a.answer, tags=[], strip=True))))
            )

        quiz_questions.append(
            QuizQuestion(
                question=html.unescape(bleach.clean(q.question, tags=ALLOWED_TAGS_FOR_QUIZ, strip=True)),
                answers=answers,
                time=str(q.time / 1000),
                image=image,
            ).dict()
        )
    cover = None
    if quiz.kahoot.cover != "":
        image_bytes = await _download_image(quiz.kahoot.cover)
        image_name = f"{quiz_id}--{uuid.uuid4()}"
        await storage.upload(file_name=image_name, file_data=image_bytes)
        cover = f"{settings.root_address}/api/v1/storage/download/{image_name}"
    quiz_data = Quiz(
        id=quiz_id,
        public=True,
        title=html.unescape(bleach.clean(quiz.kahoot.title, tags=ALLOWED_TAGS_FOR_QUIZ, strip=True)),
        description=html.unescape(bleach.clean(quiz.kahoot.description, tags=ALLOWED_TAGS_FOR_QUIZ, strip=True)),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        user_id=user.id,
        questions=json.dumps(quiz_questions),
        imported_from_kahoot=True,
        cover_image=cover,
    )
    meilisearch.index(settings.meilisearch_index).add_documents([await get_meili_data(quiz_data)])
    return await quiz_data.save()
