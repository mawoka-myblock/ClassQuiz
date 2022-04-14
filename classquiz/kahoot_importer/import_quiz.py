import html
import json
import uuid
from datetime import datetime

from aiohttp import ClientSession

from classquiz.config import settings, storage, meilisearch
from classquiz.db.models import Quiz, QuizAnswer, QuizQuestion, User
from classquiz.kahoot_importer.get import get as get_quiz
from classquiz.helpers import get_meili_data

settings = settings()


async def _download_image(url: str) -> bytes:
    async with ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.read()


# async def _upload_to_imgur(image: bytes, album_id: str | None) -> str:
#     """
#     Uploads an image to Imgur.
#     :param image: The image to upload.
#     :return: The URL of the image on Imgur.
#     """
#
#     formdata = FormData()
#     formdata.add_field('image', image, filename='image.png')
#     if album_id:
#         formdata.add_field('album', album_id)
#     async with ClientSession(headers={"Authorization": f"Client-ID {settings.imgur_client_id}"}) as session:
#         print(settings.imgur_client_id)
#         async with session.post("https://api.imgur.com/3/image", data=image) as resp:
#             data = await resp.json()
#             print(resp.headers)
#             try:
#                 return data["data"]["link"]
#             except KeyError:
#                 raise Exception(data)
#
#
# async def _generate_imgur_album(quiz_id: str) -> str:
#     # """
#     # Generates an album on Imgur.
#     # :param quiz_id: The ID of the quiz.
#     # :return: The URL of the album on Imgur.
#     # """
#     formdata = FormData()
#     formdata.add_field('title', quiz_id)
#     async with ClientSession(headers={"Authorization": f"Client-ID {settings.imgur_client_id}"}) as session:
#         async with session.post("https://api.imgur.com/3/album", data={"title": "Quiz: " + quiz_id}, ) as resp:
#             data = await resp.json()
#             return data["data"]["id"]


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

    for q in quiz.kahoot.questions:
        answers: list[QuizAnswer] = []
        image = None
        if q.image is not None and q.image != "":
            image_bytes = await _download_image(q.image)
            image_name = f"{quiz_id}--{uuid.uuid4()}"
            image = await storage.upload(file_name=image_name, file_data=image_bytes)
            image = f"{settings.root_address}/api/v1/storage/download/{image_name}"
            # image = q.image
        for a in q.choices:
            answers.append((QuizAnswer(right=a.correct, answer=html.unescape(a.answer))))
        quiz_questions.append(
            QuizQuestion(
                question=q.question,
                answers=answers,
                time=str(q.time / 1000),
                image=image,
            ).dict()
        )
    quiz_data = Quiz(
        id=quiz_id,
        public=True,
        title=quiz.kahoot.title,
        description=quiz.kahoot.description,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        user_id=user.id,
        questions=json.dumps(quiz_questions),
    )
    meilisearch.index(settings.meilisearch_index).add_documents([await get_meili_data(quiz_data)])
    return await quiz_data.save()
