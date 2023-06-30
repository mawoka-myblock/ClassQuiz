# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


from typing import Generator
from fastapi.testclient import TestClient

# from classquiz.socket_server import sio
from classquiz import app as fastapi_app

# from typing import List, Optional

# stdlib imports
# import asyncio

# 3rd party imports
import pytest

# import socketio
# import uvicorn

# FastAPI imports
# from fastapi import FastAPI

PORT = 8000


class ValueStorage:
    quiz_id = None
    imported_quizzes = []
    game_pin = None
    game_id = None
    exported_quiz_data = None
    edit_id = None
    image_id = None
    cookies = None
    file_id = None
    quiztivity_id = None
    share_id = None
    expired_share_id = None


example_quiz = {
    "public": True,
    "title": "Some test question",
    "description": "A description",
    "questions": [
        {
            "type": "ABCD",
            "question": "Is ClassQuiz cool?",
            "time": 10,
            "answers": [{"right": True, "answer": "Yes"}, {"right": False, "answer": "No"}],
        },
        {
            "type": "ABCD",
            "question": "Do you like open source?",
            "time": 5,
            "image": None,
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

example_quiztivity = {
    "title": "Some test Quiztivity",
    "pages": [
        {
            "title": "Some test question",
            "type": "ABCD",
            "data": {
                "question": "Is ClassQuiz cool?",
                "answers": [{"correct": True, "answer": "Yes"}, {"correct": False, "answer": "No"}],
            },
        }
    ],
}

# mock_test_results = {'0': [{'username': 'Player 1', 'answer': 'Byte, Bit, KB, MB, GB, TB', 'right': False},
# {'username': 'Player 2', 'answer': 'Byte, Bit, KB, MB, GB, TB', 'right': False}, {'username': 'Player 3',
# 'answer': 'Bit, Byte, KB, MB, GB, TB', 'right': True}], '1': [{'username': 'Player 3', 'answer': 'CPU',
# 'right': True}, {'username': 'Player 2', 'answer': 'CPU', 'right': True}, {'username': 'Player 1',
# 'answer': 'CPU', 'right': True}], '2': [{'username': 'Player 1', 'answer': 'Peripheriegeräte',
# 'right': True}, {'username': 'Player 2', 'answer': 'Speichergeräte', 'right': False},
# {'username': 'Player 3', 'answer': 'Kommunikationsgeräte', 'right': False}], '3': [{'username': 'Player 1',
# 'answer': 'die Taktfrequenz der CPU', 'right': True}, {'username': 'Player 2',
# 'answer': 'die Taktfrequenz der CPU', 'right': True}, {'username': 'Player 3',
# 'answer': 'die Taktfrequenz der CPU', 'right': True}], '4': [{'username': 'Player 3', 'answer': 'Drucker',
# 'right': True}, {'username': 'Player 2', 'answer': 'Drucker', 'right': True}, {'username': 'Player 1',
# 'answer': 'Tabellenkalkulation', 'right': False}], '5': [{'username': 'Player 1',
# 'answer':'CPU (Central Processing Unit)', 'right': False}, {'username': 'Player 2',
# 'answer': 'RAM (Random Access Memory)', 'right': True}, {'username': 'Player 3',
# 'answer': 'RAM (Random Access Memory)', 'right': True}], '6': [{'username': 'Player 3', 'answer': 'RAM',
# 'right': True}, {'username': 'Player 2', 'answer': 'ROM', 'right': False}, {'username': 'Player 1',
# 'answer': 'RAM', 'right': True}], '7': [{'username': 'Player 1', 'answer': '1 TB (Terabyte)',
# 'right': True}, {'username': 'Player 2', 'answer': '500 KB (Kilobyte)', 'right': False},
# {'username': 'Player 3', 'answer': '500 TB (Terabyte)', 'right': False}], '8': [{'username': 'Player 3',
# 'answer': 'Tabellenkalkulationsprogramm', 'right': True}, {'username': 'Player 2',
# 'answer': 'Tabellenkalkulationsprogramm', 'right': True}, {'username': 'Player 1', 'answer': 'Linux',
# 'right': False}], '9': [{'username': 'Player 1', 'answer': 'Anwendungsprogramme', 'right': True},
# {'username': 'Player 2', 'answer': 'Lernprogramme', 'right': False}, {'username': 'Player 3',
# 'answer': 'Anwendungsprogramme', 'right': True}]}


@pytest.fixture(scope="module")
def test_client() -> Generator:
    with TestClient(fastapi_app) as testclient:
        yield testclient


#
# sio.eio.start_service_task = False
#
#
# class UvicornTestServer(uvicorn.Server):
#     """Uvicorn test server
#
#     Usage:
#         @pytest.fixture
#         async def start_stop_server():
#             server = UvicornTestServer()
#             await server.up()
#             yield
#             await server.down()
#     """
#
#     def __init__(self, app: FastAPI = fastapi_app, host: str = '127.0.0.1', port: int = PORT):
#         """Create a Uvicorn test server
#
#         Args:
#             app (FastAPI, optional): the FastAPI app. Defaults to main.app.
#             host (str, optional): the host ip. Defaults to '127.0.0.1'.
#             port (int, optional): the port. Defaults to PORT.
#         """
#         self._startup_done = asyncio.Event()
#         super().__init__(config=uvicorn.Config(app, host=host, port=port))
#
#     async def startup(self, sockets: Optional[List] = None) -> None:
#         """Override uvicorn startup"""
#         await super().startup(sockets=sockets)
#         self.config.setup_event_loop()
#         self._startup_done.set()
#
#     async def up(self) -> None:
#         """Start up server asynchronously"""
#         self._serve_task = asyncio.create_task(self.serve())
#         await self._startup_done.wait()
#
#     async def down(self) -> None:
#         """Shut down server asynchronously"""
#         self.should_exit = True
#         await self._serve_task
#
#
#
