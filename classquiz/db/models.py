import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Json
from . import metadata, database
import ormar


class User(ormar.Model):
    """
    The user model
    """
    id: uuid.UUID = ormar.UUID(primary_key=True, default=uuid.uuid4())
    email: str = ormar.String(unique=True, max_length=100)
    username: str = ormar.String(unique=True, max_length=100)
    password: str = ormar.String(unique=True, max_length=100)
    verified: bool = ormar.Boolean(default=False)
    verify_key: str = ormar.String(unique=True, max_length=100, nullable=True)
    created_at: datetime = ormar.DateTime(default=datetime.now())

    class Meta:
        tablename = 'users'
        metadata = metadata
        database = database


class UserSession(ormar.Model):
    """
    The user session model
    """
    id: uuid.UUID = ormar.UUID(primary_key=True, default=uuid.uuid4())
    user: uuid.UUID = ormar.ForeignKey(User)
    session_key: str = ormar.String(unique=True, max_length=64)
    created_at: datetime = ormar.DateTime(default=datetime.now())
    ip_address: str = ormar.String(max_length=100, nullable=True)
    user_agent: str = ormar.String(max_length=255, nullable=True)
    last_seen: datetime = ormar.DateTime(default=datetime.now())

    class Meta:
        tablename = 'user_sessions'
        metadata = metadata
        database = database


class QuizAnswer(BaseModel):
    right: bool
    answer: str


class QuizQuestion(BaseModel):
    question: str
    time: str  # in Secs
    answers: list[QuizAnswer]


class QuizInput(BaseModel):
    public: bool = False
    title: str
    description: str
    questions: list[QuizQuestion]


class Quiz(ormar.Model):
    id: uuid.UUID = ormar.UUID(primary_key=True, default=uuid.uuid4(), nullable=False, unique=True)
    public: bool = ormar.Boolean(default=False)
    title: str = ormar.String(max_length=100)
    description: str = ormar.String(max_length=300, nullable=True)
    created_at: datetime = ormar.DateTime(default=datetime.now())
    updated_at: datetime = ormar.DateTime(default=datetime.now())
    user_id: uuid.UUID = ormar.UUID(foreign_key=User.id)
    questions: Json[list[QuizQuestion]] = ormar.JSON(nullable=False)

    class Meta:
        tablename = 'quiz'
        metadata = metadata
        database = database


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None


class PlayGame(BaseModel):
    quiz_id: uuid.UUID | str
    description: str
    title: str
    questions: list[QuizQuestion]
    game_id: uuid.UUID
    game_pin: str
    started: bool = False


class GamePlayer(BaseModel):
    username: str
    sid: str


class GameAnser2(BaseModel):
    username: str
    right: bool
    answer: str


class GameAnser1(BaseModel):
    id: int
    answers: list[GameAnser2]


class GameSession(BaseModel):
    admin: str
    game_id: str
    players: list[GamePlayer | None]
    answers: list[GameAnser1 | None]
