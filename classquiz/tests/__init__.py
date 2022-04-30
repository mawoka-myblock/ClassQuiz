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


example_quiz = {
    "public": True,
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
