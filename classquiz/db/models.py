# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import os
import uuid
from datetime import datetime
from typing import Optional

import ormar
from ormar import ReferentialAction
from pydantic import BaseModel, Json, validator, RootModel
from enum import Enum
from . import metadata, database
from .quiztivity import QuizTivityPage
from sqlalchemy import func


class UserAuthTypes(Enum):
    LOCAL = "LOCAL"
    GOOGLE = "GOOGLE"
    GITHUB = "GITHUB"
    CUSTOM = "CUSTOM"


class User(ormar.Model):
    """
    The user model in the database
    """

    id: uuid.UUID = ormar.UUID(primary_key=True, default=uuid.uuid4())
    email: str = ormar.String(unique=True, max_length=100)
    username: str = ormar.String(unique=True, max_length=100)
    password: Optional[str] = ormar.String(max_length=100, nullable=True)
    verified: bool = ormar.Boolean(default=False)
    verify_key: str = ormar.String(unique=True, max_length=100, nullable=True)
    created_at: datetime = ormar.DateTime(default=datetime.now())
    auth_type: UserAuthTypes = ormar.Enum(enum_class=UserAuthTypes, default=UserAuthTypes.LOCAL)
    google_uid: Optional[str] = ormar.String(unique=True, max_length=255, nullable=True)
    avatar: bytes = ormar.LargeBinary(max_length=25000, represent_as_base64_str=True)
    github_user_id: int | None = ormar.Integer(nullable=True)
    require_password: bool = ormar.Boolean(default=True, nullable=False)
    backup_code: str = ormar.String(max_length=64, min_length=64, nullable=False, default=os.urandom(32).hex())
    totp_secret: str = ormar.String(max_length=32, min_length=32, nullable=True, default=None)
    storage_used: int = ormar.BigInteger(nullable=False, default=0, minimum=0)

    ormar_config = ormar.OrmarConfig(database=database, metadata=metadata, tablename="users")


class FidoCredentials(ormar.Model):
    pk: int = ormar.Integer(autoincrement=True, primary_key=True)
    id: bytes = ormar.LargeBinary(max_length=256)
    public_key: bytes = ormar.LargeBinary(max_length=256)
    sign_count: int = ormar.Integer()
    user: Optional[User] = ormar.ForeignKey(User, ondelete=ReferentialAction.CASCADE)

    ormar_config = ormar.OrmarConfig(database=database, metadata=metadata, tablename="fido_credentials")


class ApiKey(ormar.Model):
    key: str = ormar.String(max_length=48, min_length=48, primary_key=True)
    user: Optional[User] = ormar.ForeignKey(User, ondelete=ReferentialAction.CASCADE)

    ormar_config = ormar.OrmarConfig(database=database, metadata=metadata, tablename="api_keys")


class UserSession(ormar.Model):
    """
    The user session model for user-sessions
    """

    id: uuid.UUID = ormar.UUID(primary_key=True, default=uuid.uuid4())
    user: Optional[User] = ormar.ForeignKey(User, ondelete=ReferentialAction.CASCADE)
    session_key: str = ormar.String(unique=True, max_length=64)
    created_at: datetime = ormar.DateTime(default=datetime.now())
    ip_address: str = ormar.String(max_length=100, nullable=True)
    user_agent: str = ormar.String(max_length=255, nullable=True)
    last_seen: datetime = ormar.DateTime(default=datetime.now())

    ormar_config = ormar.OrmarConfig(database=database, metadata=metadata, tablename="user_sessions")


class ABCDQuizAnswer(BaseModel):
    right: bool
    answer: str
    color: str | None = None


class RangeQuizAnswer(BaseModel):
    min: int
    max: int
    min_correct: int
    max_correct: int


class VotingQuizAnswer(BaseModel):
    answer: str
    image: str | None = None
    color: str | None = None


class QuizQuestionType(str, Enum):
    ABCD = "ABCD"
    RANGE = "RANGE"
    VOTING = "VOTING"
    SLIDE = "SLIDE"
    TEXT = "TEXT"
    ORDER = "ORDER"
    CHECK = "CHECK"


class TextQuizAnswer(BaseModel):
    answer: str
    case_sensitive: bool


class QuizQuestion(BaseModel):
    question: str
    time: str  # in Secs
    type: None | QuizQuestionType = QuizQuestionType.ABCD
    answers: list[ABCDQuizAnswer] | RangeQuizAnswer | list[TextQuizAnswer] | list[VotingQuizAnswer] | str
    image: str | None = None
    hide_results: bool | None = False

    @validator("answers")
    def answers_not_none_if_abcd_type(cls, v, values):
        if values["type"] == QuizQuestionType.ABCD and not isinstance(v[0], ABCDQuizAnswer):
            raise ValueError("Answers can't be none if type is ABCD")
        if values["type"] == QuizQuestionType.RANGE and not isinstance(v, RangeQuizAnswer):
            raise ValueError("Answer must be from type RangeQuizAnswer if type is RANGE")
        if values["type"] == QuizQuestionType.VOTING and not isinstance(v[0], VotingQuizAnswer):
            raise ValueError("Answer must be from type VotingQuizAnswer if type is VOTING")
        if values["type"] == QuizQuestionType.TEXT and not isinstance(v[0], TextQuizAnswer):
            raise ValueError("Answer must be from type TextQuizAnswer if type is TEXT")
        if values["type"] == QuizQuestionType.ORDER and not isinstance(v[0], VotingQuizAnswer):
            raise ValueError("Answer must be from type VotingQuizAnswer if type is ORDER")
        if values["type"] == QuizQuestionType.SLIDE and not isinstance(v, str):
            raise ValueError("Answer must be from type SlideElement if type is SLIDE")
        if values["type"] == QuizQuestionType.CHECK and not isinstance(v[0], ABCDQuizAnswer):
            raise ValueError("Answers can't be none if type is CHECK")
        return v


class QuizInput(BaseModel):
    public: bool = False
    title: str
    description: str
    cover_image: str | None = None
    background_color: str | None = None
    questions: list[QuizQuestion]
    background_image: str | None = None


class Quiz(ormar.Model):
    id: uuid.UUID = ormar.UUID(primary_key=True, default=uuid.uuid4(), nullable=False, unique=True)
    public: bool = ormar.Boolean(default=False)
    title: str = ormar.Text()
    description: str = ormar.Text(nullable=True)
    created_at: datetime = ormar.DateTime(default=datetime.now())
    updated_at: datetime = ormar.DateTime(default=datetime.now())
    user_id: uuid.UUID = ormar.ForeignKey(User, ondelete=ReferentialAction.CASCADE)
    questions: Json[list[QuizQuestion]] = ormar.JSON(nullable=False)
    imported_from_kahoot: Optional[bool] = ormar.Boolean(default=False, nullable=True)
    cover_image: Optional[str] = ormar.Text(nullable=True, unique=False)
    background_color: str | None = ormar.Text(nullable=True, unique=False)
    background_image: str | None = ormar.Text(nullable=True, unique=False)
    kahoot_id: uuid.UUID | None = ormar.UUID(nullable=True, default=None)
    likes: int = ormar.Integer(nullable=False, default=0, server_default="0")
    dislikes: int = ormar.Integer(nullable=False, default=0, server_default="0")
    plays: int = ormar.Integer(nullable=False, default=0, server_default="0")
    views: int = ormar.Integer(nullable=False, default=0, server_default="0")
    mod_rating: int | None = ormar.SmallInteger(nullable=True)

    ormar_config = ormar.OrmarConfig(tablename="quiz", metadata=metadata, database=database)


class InstanceData(ormar.Model):
    instance_id: uuid.UUID = ormar.UUID(primary_key=True, default=uuid.uuid4(), nullable=False, unique=True)

    ormar_config = ormar.OrmarConfig(tablename="instance_data", metadata=metadata, database=database)


class Token(BaseModel):
    """
    For JWT
    """

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    For JWT
    """

    email: str | None = None


class PlayGame(BaseModel):
    quiz_id: uuid.UUID | str
    description: str
    user_id: uuid.UUID
    title: str
    questions: list[QuizQuestion]
    game_id: uuid.UUID
    game_pin: str
    started: bool = False
    captcha_enabled: bool = False
    cover_image: str | None = None
    game_mode: str | None = None
    current_question: int = -1
    background_color: str | None = None
    background_image: str | None = None
    custom_field: str | None = None
    question_show: bool = False


class GamePlayer(BaseModel):
    username: str
    sid: str | None = None


class GameAnswer2(BaseModel):
    username: str
    right: bool
    answer: str


class GameAnswer1(BaseModel):
    id: int
    answers: list[GameAnswer2]


class GameSession(BaseModel):
    admin: str
    game_id: str
    # players: list[GamePlayer | None]
    answers: list[GameAnswer1 | None]


class UpdatePassword(BaseModel):
    old_password: str
    new_password: str


class AnswerData(BaseModel):
    username: str
    answer: str
    right: bool
    time_taken: float  # In milliseconds
    score: int


class AnswerDataList(RootModel):
    # Just a method to make a top-level list
    root: list[AnswerData]


class GameInLobby(BaseModel):
    game_pin: str
    quiz_title: str
    game_id: uuid.UUID


# skipcq: PY-W0069
# class UserProfileLinks(ormar.Model):
#     id: int = ormar.Integer(primary_key=True, autoincrement=True)
#     user: Optional[User] = ormar.ForeignKey(User)
#     github_username: str | None = ormar.Text(nullable=True)
#     reddit_username: str | None = ormar.Text(nullable=True)
#     kahoot_user_id: str | None = ormar.Text(nullable=True)


class GameResults(ormar.Model):
    id: uuid.UUID = ormar.UUID(primary_key=True)
    quiz: uuid.UUID | Quiz = ormar.ForeignKey(Quiz, ondelete=ReferentialAction.CASCADE)
    user: uuid.UUID | User = ormar.ForeignKey(User, ondelete=ReferentialAction.CASCADE)
    timestamp: datetime = ormar.DateTime(default=datetime.now(), nullable=False)
    player_count: int = ormar.Integer(nullable=False, default=0)
    note: str | None = ormar.Text(nullable=True)
    answers: Json[list[AnswerData]] = ormar.JSON(True)
    player_scores: Json[dict[str, str]] = ormar.JSON(nullable=True)
    custom_field_data: Json[dict[str, str]] | None = ormar.JSON(nullable=True)
    title: str = ormar.Text(nullable=False)
    description: str = ormar.Text(nullable=False)
    questions: Json[list[QuizQuestion]] = ormar.JSON(nullable=False)

    ormar_config = ormar.OrmarConfig(database=database, metadata=metadata, tablename="game_results")


class QuizTivityInput(BaseModel):
    title: str
    pages: list[QuizTivityPage]


class QuizTivity(ormar.Model):
    id: uuid.UUID = ormar.UUID(primary_key=True)
    title: str = ormar.Text(nullable=False)
    created_at: datetime = ormar.DateTime(nullable=False, server_default=func.now())
    user: User | None = ormar.ForeignKey(User, ondelete=ReferentialAction.CASCADE)
    pages: list[QuizTivityPage] = ormar.JSON(nullable=False)

    ormar_config = ormar.OrmarConfig(tablename="quiztivitys", metadata=metadata, database=database)


class QuizTivityShare(ormar.Model):
    id: uuid.UUID = ormar.UUID(primary_key=True)
    name: str | None = ormar.Text(nullable=True)
    expire_at: datetime | None = ormar.DateTime(nullable=True)
    quiztivity: QuizTivity | None = ormar.ForeignKey(QuizTivity, ondelete=ReferentialAction.CASCADE)
    user: User | None = ormar.ForeignKey(User, ondelete=ReferentialAction.CASCADE)

    ormar_config = ormar.OrmarConfig(database=database, metadata=metadata, tablename="quiztivityshares")


class OnlyId(BaseModel):
    id: uuid.UUID


class PublicQuizTivityShare(BaseModel):
    id: uuid.UUID
    name: str | None = None
    expire_in: int | None = None
    quiztivity: OnlyId
    user: OnlyId

    @classmethod
    def from_db_model(cls, data: QuizTivityShare):
        expire_in = None
        if data.expire_at is not None:
            expire_in = int((data.expire_at - datetime.now()).seconds / 60)
        return cls(
            id=data.id,
            name=data.name,
            expire_in=expire_in,
            quiztivity=OnlyId(id=data.quiztivity.id),
            user=OnlyId(id=data.user.id),
        )


class StorageItem(ormar.Model):
    id: uuid.UUID = ormar.UUID(primary_key=True)
    uploaded_at: datetime = ormar.DateTime(nullable=False, default=datetime.now())
    mime_type: str = ormar.Text(nullable=False)
    hash: bytes | None = ormar.LargeBinary(nullable=True, min_length=16, max_length=16)
    user: User | None = ormar.ForeignKey(User, ondelete=ReferentialAction.SET_NULL)
    size: int = ormar.BigInteger(nullable=False)
    storage_path: str | None = ormar.Text(nullable=True)
    deleted_at: datetime | None = ormar.DateTime(nullable=True, default=None)
    quiztivities: list[QuizTivity] | None = ormar.ManyToMany(QuizTivity)
    quizzes: list[Quiz] | None = ormar.ManyToMany(Quiz)
    alt_text: str | None = ormar.Text(default=None, nullable=True)
    filename: str | None = ormar.Text(default=None, nullable=True)
    thumbhash: str | None = ormar.Text(default=None, nullable=True)
    server: str | None = ormar.Text(default=None, nullable=True)
    imported: bool = ormar.Boolean(default=False, nullable=True)

    ormar_config = ormar.OrmarConfig(database=database, metadata=metadata, tablename="storage_items")


class PublicStorageItem(BaseModel):
    id: uuid.UUID
    uploaded_at: datetime
    mime_type: str
    hash: str | None = None
    size: int
    deleted_at: datetime | None = None
    alt_text: str | None = None
    filename: str | None = None
    thumbhash: str | None = None
    server: str | None = None
    imported: bool

    @classmethod
    def from_db_model(cls, data: StorageItem):
        hash_data = None
        if data.hash is not None:
            hash_data = data.hash.hex()
        return cls(
            id=data.id,
            uploaded_at=data.uploaded_at,
            mime_type=data.mime_type,
            hash=hash_data,
            size=data.size,
            deleted_at=data.deleted_at,
            alt_text=data.alt_text,
            filename=data.filename,
            thumbhash=data.thumbhash,
            server=data.server,
            imported=data.imported,
        )


class PrivateStorageItem(PublicStorageItem):
    quizzes: list[OnlyId]
    quiztivities: list[OnlyId]

    @classmethod
    def from_db_model(cls, data: StorageItem):
        hash_data = None
        if data.hash is not None:
            hash_data = data.hash.hex()
        quiztivities = []
        quizzes = []
        for quiz in data.quizzes:
            quizzes.append(OnlyId(id=quiz.id))
        for quiztivity in data.quiztivities:
            quiztivities.append(OnlyId(id=quiztivity.id))
        return cls(
            id=data.id,
            uploaded_at=data.uploaded_at,
            mime_type=data.mime_type,
            hash=hash_data,
            size=data.size,
            deleted_at=data.deleted_at,
            alt_text=data.alt_text,
            filename=data.filename,
            quiztivities=quiztivities,
            quizzes=quizzes,
            thumbhash=data.thumbhash,
            server=data.server,
            imported=data.imported,
        )


class UpdateStorageItem(BaseModel):
    filename: str | None = None
    alt_text: str | None = None


class Controller(ormar.Model):
    id: uuid.UUID = ormar.UUID(primary_key=True)
    user: uuid.UUID | User = ormar.ForeignKey(User)
    secret_key: str = ormar.String(nullable=False, max_length=24, min_length=24)
    player_name: str = ormar.Text(nullable=False)
    last_seen: datetime | None = ormar.DateTime(nullable=True)
    first_seen: datetime | None = ormar.DateTime(nullable=True)
    name: str = ormar.Text(nullable=False)
    os_version: str | None = ormar.Text(nullable=True)
    wanted_os_version: str = ormar.Text(nullable=True, default=None)

    ormar_config = ormar.OrmarConfig(tablename="controller", metadata=metadata, database=database)


class Rating(ormar.Model):
    id: uuid.UUID = ormar.UUID(primary_key=True)
    user: uuid.UUID | User = ormar.ForeignKey(User)
    positive: bool = ormar.Boolean(nullable=False)
    created_at: datetime = ormar.DateTime(nullable=False, server_default=func.now())
    quiz: uuid.UUID | Quiz = ormar.ForeignKey(Quiz)

    ormar_config = ormar.OrmarConfig(database=database, metadata=metadata, tablename="rating")
