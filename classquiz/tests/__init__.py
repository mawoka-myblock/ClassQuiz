import pytest
from typing import Generator
from fastapi.testclient import TestClient
from classquiz import app


class ValueStorage:
    quiz_id = None
    imported_quizzes = [None]


example_quiz = {
    "public": False,
    "title": "Some test question",
    "description": "A description",
    "questions": [
        {
            "question": "Is ClassQuiz cool?",
            "time": 10,
            "answers": [{"right": True, "answer": "Yes"}, {"right": False, "answer": "No"}],
        },
        {
            "question": "Do you like open source?",
            "time": 5,
            "image": "https://i.imgur.com/sSNSy77.png",
            "answers": [
                {"right": True, "answer": "Yes"},
                {"right": False, "answer": "No"},
                {"right": False, "answer": "Maybe"},
            ],
        },
    ],
}
test_user_email = "sth@byom.de"
test_user_password = "test"


@pytest.fixture(scope="module")
def test_client() -> Generator:
    with TestClient(app) as testclient:
        yield testclient
