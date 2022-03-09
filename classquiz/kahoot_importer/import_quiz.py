import json
import uuid
from datetime import datetime

from aiohttp import ClientSession
import pydantic
from classquiz.db.models import Quiz, QuizAnswer, QuizQuestion, User
from classquiz.kahoot_importer.get import get as get_quiz


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

    for q in quiz.kahoot.questions:
        answers: list[QuizAnswer] = []
        for a in q.choices:
            answers.append((QuizAnswer(right=a.correct, answer=a.answer)))
        quiz_questions.append(QuizQuestion(question=q.question, answers=answers, time=str(q.time / 1000)).dict())
    quiz_data = Quiz(id=uuid.uuid4(), public=False, title=quiz.kahoot.title, description=quiz.kahoot.description,
                     created_at=datetime.now(), updated_at=datetime.now(), user_id=user.id,
                     questions=json.dumps(quiz_questions))
    return await quiz_data.save()
