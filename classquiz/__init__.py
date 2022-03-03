from fastapi import FastAPI
from classquiz.socket_server import sio
from socketio import ASGIApp

from classquiz.routers import users, quiz, utils
from classquiz.db import database

app = FastAPI()
app.state.database = database


@app.on_event("startup")
async def startup() -> None:
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()


app.include_router(users.router, tags=["users"], prefix="/api/v1/users")
app.include_router(quiz.router, tags=["quiz"], prefix="/api/v1/quiz")
app.include_router(utils.router, tags=["utils"], prefix="/api/v1/utils")
app.mount("/", ASGIApp(sio))
