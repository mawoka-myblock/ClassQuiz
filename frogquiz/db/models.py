# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
# SPDX-FileCopyrightText: 2026 frogQuiz contributors
#
# SPDX-License-Identifier: MPL-2.0
from __future__ import annotations


import hashlib
import html
import os
import uuid
from datetime import datetime
from typing import Optional, Self
from frogquiz.config import redis
import json

import bleach
import ormar
from ormar import ReferentialAction
from pydantic import (
    BaseModel,
    Field,
    Json,
    field_validator,
    ConfigDict,
    RootModel,
    ValidationInfo,
)
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

    id: uuid.UUID = ormar.UUID(primary_key=True, default=uuid.uuid4)
    email: str = ormar.String(unique=True, max_length=100)
    username: str = ormar.String(unique=True, max_length=100)
    password: Optional[str] = ormar.String(max_length=100, nullable=True)
    verified: bool = ormar.Boolean(default=False)
    # Explicit, rather than "whoever has the oldest created_at". That rule silently
    # handed the instance to the next-oldest account whenever the admin deleted
    # theirs -- and account deletion is reachable from the UI now.
    is_admin: bool = ormar.Boolean(default=False, nullable=False)
    verify_key: str = ormar.String(unique=True, max_length=100, nullable=True)
    created_at: datetime = ormar.DateTime(default=datetime.now)
    auth_type: UserAuthTypes = ormar.Enum(enum_class=UserAuthTypes, default=UserAuthTypes.LOCAL)
    google_uid: Optional[str] = ormar.String(unique=True, max_length=255, nullable=True)
    avatar: bytes = ormar.LargeBinary(max_length=25000, represent_as_base64_str=True)
    github_user_id: int | None = ormar.Integer(nullable=True)
    require_password: bool = ormar.Boolean(default=True, nullable=False)
    # Stored as a hash, like session keys: it's only ever compared for equality,
    # and this placeholder is unusable anyway until /2fa/backup_code reveals a real one.
    backup_code: str = ormar.String(
        max_length=64, min_length=64, nullable=False, default=lambda: hashlib.sha256(os.urandom(32)).hexdigest()
    )
    totp_secret: str = ormar.String(max_length=32, min_length=32, nullable=True, default=None)
    storage_used: int = ormar.BigInteger(nullable=False, default=0, minimum=0)

    ormar_config = ormar.OrmarConfig(
        tablename="users",
        metadata=metadata,
        database=database,
    )

    model_config = ConfigDict(use_enum_values=True)


class FidoCredentials(ormar.Model):
    pk: int = ormar.Integer(autoincrement=True, primary_key=True)
    id: bytes = ormar.LargeBinary(max_length=256)
    public_key: bytes = ormar.LargeBinary(max_length=256)
    sign_count: int = ormar.Integer()
    user: Optional[User] = ormar.ForeignKey(User, ondelete=ReferentialAction.CASCADE)

    ormar_config = ormar.OrmarConfig(
        tablename="fido_credentials",
        metadata=metadata,
        database=database,
    )


class ApiKey(ormar.Model):
    key: str = ormar.String(max_length=48, min_length=48, primary_key=True)
    user: Optional[User] = ormar.ForeignKey(User, ondelete=ReferentialAction.CASCADE)

    ormar_config = ormar.OrmarConfig(
        tablename="api_keys",
        metadata=metadata,
        database=database,
    )


class UserSession(ormar.Model):
    """
    The user session model for user-sessions
    """

    id: uuid.UUID = ormar.UUID(primary_key=True, default=uuid.uuid4)
    user: Optional[User] = ormar.ForeignKey(User, ondelete=ReferentialAction.CASCADE)
    session_key: str = ormar.String(unique=True, max_length=64)
    created_at: datetime = ormar.DateTime(default=datetime.now)
    ip_address: str = ormar.String(max_length=100, nullable=True)
    user_agent: str = ormar.String(max_length=255, nullable=True)
    last_seen: datetime = ormar.DateTime(default=datetime.now)

    ormar_config = ormar.OrmarConfig(
        tablename="user_sessions",
        metadata=metadata,
        database=database,
    )


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

    @field_validator("answers")
    def answers_not_none_if_abcd_type(cls, v, info: ValidationInfo):
        # Every branch below reads v[0]. An empty list used to reach it and raise
        # IndexError, which is not a validation error, so the API answered 500.
        if isinstance(v, list) and len(v) == 0:
            raise ValueError("A question needs at least one answer")
        if info.data["type"] == QuizQuestionType.ABCD and not isinstance(v[0], ABCDQuizAnswer):
            raise ValueError("Answers can't be none if type is ABCD")
        if info.data["type"] == QuizQuestionType.RANGE and not isinstance(v, RangeQuizAnswer):
            raise ValueError("Answer must be from type RangeQuizAnswer if type is RANGE")
        if info.data["type"] == QuizQuestionType.VOTING and not isinstance(v[0], VotingQuizAnswer):
            raise ValueError("Answer must be from type VotingQuizAnswer if type is VOTING")
        if info.data["type"] == QuizQuestionType.TEXT and not isinstance(v[0], TextQuizAnswer):
            raise ValueError("Answer must be from type TextQuizAnswer if type is TEXT")
        if info.data["type"] == QuizQuestionType.ORDER and not isinstance(v[0], VotingQuizAnswer):
            raise ValueError("Answer must be from type VotingQuizAnswer if type is ORDER")
        if info.data["type"] == QuizQuestionType.SLIDE and not isinstance(v, str):
            raise ValueError("Answer must be from type SlideElement if type is SLIDE")
        if info.data["type"] == QuizQuestionType.CHECK and not isinstance(v[0], ABCDQuizAnswer):
            raise ValueError("Answers can't be none if type is CHECK")
        return v


# Bounds for what a client may save. They live on QuizInput rather than QuizQuestion on
# purpose: QuizQuestion also parses quizzes already in the database and in live games,
# and tightening it would make an old quiz with an odd value unloadable instead of just
# unsaveable-until-fixed. The editor's own timer field is 1-999.
MAX_QUESTION_SECONDS = 999
# Not the editor's cap of four. A Kahoot import can bring six answers, and a cap of four
# would make such a quiz impossible to re-save. Ten is the real limit: multiple-answer
# questions are scored by concatenating option indices ("02"), which is only
# unambiguous while every index is one digit.
MAX_ANSWERS_PER_QUESTION = 10
# A DoS ceiling, not a product limit. With no bound a quiz JSON could be arbitrarily large
# -- a million questions is ~140MB parsed into memory on save and held as PlayGame state in
# Redis per live game. 1000 bounds that at ~140KB while staying well clear of real use:
# api-edge.e2e.ts deliberately proves a 500-question quiz saves and starts, and the editor
# caps its own at 50 (yupSchemas.ts) for UX, so this is not the user-facing limit and the
# two are meant to differ. Was briefly 100, which wrongly broke those 200/500 scale tests.
MAX_QUESTIONS_PER_QUIZ = 1000

# Text bounds, added 2026-10-02 after a deliberate attempt to break the app with hostile
# input. There were none: `ormar.Text()` is unbounded, and a 5000-character title saved
# and stored intact. Rendering is where it hurts, not storage -- a 272-character title
# with no spaces in it overflowed the player's lobby by 6611px at 390, and the same text
# as a question and an answer overflowed the host's screen by 7736px at 1440. One person
# typing that into a quiz breaks the screen for the whole room.
#
# The numbers are ours and deliberately generous: a quiz that reads well on a projector
# is far shorter than any of these, and they exist to stop the pathological case rather
# than to style anyone's writing. The CSS was hardened in the same change, so an already
# stored long value cannot break a layout either -- these two defences are independent on
# purpose, because quizzes saved before today are not revalidated.
MAX_TITLE_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 500
MAX_QUESTION_LENGTH = 250
MAX_ANSWER_LENGTH = 100


def _visible_length(value: str) -> int:
    """How long a rich-text value reads, ignoring the markup around it.

    Titles and question text come from the editor as HTML (`<p>What is <b>2</b>?</p>`),
    so counting the raw string would spend a user's budget on tags they never typed, and
    would let the same visible text pass or fail depending on its formatting.
    """
    return len(html.unescape(bleach.clean(value, tags=[], strip=True)).strip())


class QuizInput(BaseModel):
    public: bool | None = False
    title: str
    description: str
    cover_image: str | None = None
    background_color: str | None = None
    questions: list[QuizQuestion]
    background_image: str | None = None

    @field_validator("questions")
    def questions_are_playable(cls, questions: list[QuizQuestion]) -> list[QuizQuestion]:
        # A quiz with no questions saved and then started a live game with nothing in it.
        if len(questions) == 0:
            raise ValueError("A quiz needs at least one question")
        if len(questions) > MAX_QUESTIONS_PER_QUIZ:
            raise ValueError(f"A quiz can have at most {MAX_QUESTIONS_PER_QUIZ} questions")
        for i, q in enumerate(questions, start=1):
            # The game does int(float(time)) when scoring, so a non-numeric timer used to
            # save fine and then make every correct answer to that question score nothing.
            try:
                seconds = float(q.time)
            except ValueError:
                raise ValueError(f"Question {i}: the time must be a number of seconds")
            if not 1 <= seconds <= MAX_QUESTION_SECONDS:
                raise ValueError(f"Question {i}: the time must be between 1 and {MAX_QUESTION_SECONDS} seconds")
            if isinstance(q.answers, list) and len(q.answers) > MAX_ANSWERS_PER_QUESTION:
                raise ValueError(f"Question {i}: at most {MAX_ANSWERS_PER_QUESTION} answers")
            if _visible_length(q.question) > MAX_QUESTION_LENGTH:
                raise ValueError(f"Question {i}: the question must be at most {MAX_QUESTION_LENGTH} characters")
            if isinstance(q.answers, list):
                for a, answer in enumerate(q.answers, start=1):
                    text = getattr(answer, "answer", None)
                    # RANGE answers carry bounds rather than text, and a SLIDE's answer is
                    # a string body; neither is rendered as an answer tile.
                    if isinstance(text, str) and _visible_length(text) > MAX_ANSWER_LENGTH:
                        raise ValueError(f"Question {i}, answer {a}: must be at most {MAX_ANSWER_LENGTH} characters")
        return questions

    @field_validator("title")
    def title_fits_a_screen(cls, v: str) -> str:
        if _visible_length(v) > MAX_TITLE_LENGTH:
            raise ValueError(f"The title must be at most {MAX_TITLE_LENGTH} characters")
        return v

    @field_validator("description")
    def description_fits_a_screen(cls, v: str) -> str:
        if _visible_length(v) > MAX_DESCRIPTION_LENGTH:
            raise ValueError(f"The description must be at most {MAX_DESCRIPTION_LENGTH} characters")
        return v


class Quiz(ormar.Model):
    id: uuid.UUID = ormar.UUID(primary_key=True, default=uuid.uuid4, nullable=False, unique=True)
    public: bool = ormar.Boolean(default=False)
    title: str = ormar.Text()
    description: str = ormar.Text(nullable=True)
    created_at: datetime = ormar.DateTime(default=datetime.now)
    updated_at: datetime = ormar.DateTime(default=datetime.now)
    user_id: uuid.UUID | None = ormar.ForeignKey(User, ondelete=ReferentialAction.CASCADE, nullable=True)
    questions: Json[list[QuizQuestion]] = ormar.JSON(nullable=False)
    imported_from_kahoot: Optional[bool] = ormar.Boolean(default=False, nullable=True)
    cover_image: Optional[str] = ormar.Text(nullable=True, unique=False)
    background_color: str | None = ormar.Text(nullable=True, unique=False)
    background_image: str | None = ormar.Text(nullable=True, unique=False)
    kahoot_id: uuid.UUID | None = ormar.UUID(nullable=True, default=None)
    # Set only for a quiz created without an account: sha256 of the secret the
    # creator's browser holds, and when the row should be swept up if no one
    # claims it. Both are cleared once a signed-in user claims the quiz.
    anon_secret: str | None = ormar.Text(nullable=True, unique=False)
    expire_at: datetime | None = ormar.DateTime(nullable=True)
    likes: int = ormar.Integer(nullable=False, default=0, server_default="0")
    dislikes: int = ormar.Integer(nullable=False, default=0, server_default="0")
    plays: int = ormar.Integer(nullable=False, default=0, server_default="0")
    views: int = ormar.Integer(nullable=False, default=0, server_default="0")
    mod_rating: int | None = ormar.SmallInteger(nullable=True)

    ormar_config = ormar.OrmarConfig(
        tablename="quiz",
        metadata=metadata,
        database=database,
    )


class InstanceData(ormar.Model):
    instance_id: uuid.UUID = ormar.UUID(primary_key=True, default=uuid.uuid4, nullable=False, unique=True)

    ormar_config = ormar.OrmarConfig(
        tablename="instance_data",
        metadata=metadata,
        database=database,
    )


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
    user_id: uuid.UUID | None
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

    @classmethod
    async def get_from_redis(self, game_pin: str) -> Self:
        redis_data: str = await redis.get(f"game:{game_pin}")
        data = self.model_validate_json(redis_data)
        return data

    async def save(self, game_pin: str, ex: int = 7200):
        await redis.set(f"game:{game_pin}", self.model_dump_json(), ex=ex)

    def to_player_data(self) -> dict:
        return (
            {
                # game_id is the host's credential: register_as_admin and
                # register_as_remote hand the game to whoever presents it. It was
                # sent to every player on join, which made any player a host.
                **json.loads(self.model_dump_json(exclude={"quiz_id", "questions", "user_id", "game_id"})),
                "question_count": len(self.questions),
            },
        )


class GamePlayer(BaseModel):
    username: str
    sid: str | None = None

    async def to_player_stack(self, game_pin: str):
        await redis.sadd(
            f"game_session:{game_pin}:players",
            self.model_dump_json(),
        )


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

    @classmethod
    async def get_from_redis(self, game_pin: str) -> Self:
        redis_data = await redis.get(f"game_session:{game_pin}")
        return self.model_validate_json(redis_data)

    async def save(self, game_pin: str, ex: int = 7200):
        await redis.set(
            f"game_session:{game_pin}",
            self.model_dump_json(),
            ex=7200,
        )


class UpdatePassword(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8, max_length=100)


class AnswerData(BaseModel):
    username: str
    answer: str
    right: bool
    time_taken: float  # In milliseconds
    score: int


class AnswerDataList(RootModel):
    root: list[AnswerData]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]

    def append(self, item):
        self.root.append(item)

    def __len__(self) -> int:
        return len(self.root)

    @classmethod
    async def get_redis_or_empty(self, game_pin: str, question_number: str) -> Self:
        redis_res = await redis.get(f"game_session:{game_pin}:{question_number}")
        if redis_res is None:
            return self([])
        else:
            return self.model_validate_json(redis_res)


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
    user: uuid.UUID | User | None = ormar.ForeignKey(User, ondelete=ReferentialAction.CASCADE, nullable=True)
    timestamp: datetime = ormar.DateTime(default=datetime.now, nullable=False)
    player_count: int = ormar.Integer(nullable=False, default=0)
    note: str | None = ormar.Text(nullable=True)
    answers: Json[list[AnswerData]] = ormar.JSON(True)
    player_scores: Json[dict[str, str]] = ormar.JSON(nullable=True)
    custom_field_data: Json[dict[str, str]] | None = ormar.JSON(nullable=True)
    title: str = ormar.Text(nullable=False)
    description: str = ormar.Text(nullable=False)
    questions: Json[list[QuizQuestion]] = ormar.JSON(nullable=False)

    ormar_config = ormar.OrmarConfig(
        tablename="game_results",
        metadata=metadata,
        database=database,
    )


class QuizTivityInput(BaseModel):
    title: str
    pages: list[QuizTivityPage]


class QuizTivity(ormar.Model):
    id: uuid.UUID = ormar.UUID(primary_key=True)
    title: str = ormar.Text(nullable=False)
    created_at: datetime = ormar.DateTime(nullable=False, server_default=func.now())
    user: User | None = ormar.ForeignKey(User, ondelete=ReferentialAction.CASCADE)
    pages: list[QuizTivityPage] = ormar.JSON(nullable=False)

    ormar_config = ormar.OrmarConfig(
        tablename="quiztivitys",
        metadata=metadata,
        database=database,
    )


class QuizTivityShare(ormar.Model):
    id: uuid.UUID = ormar.UUID(primary_key=True)
    name: str | None = ormar.Text(nullable=True)
    expire_at: datetime | None = ormar.DateTime(nullable=True)
    quiztivity: QuizTivity | None = ormar.ForeignKey(QuizTivity, ondelete=ReferentialAction.CASCADE)
    user: User | None = ormar.ForeignKey(User, ondelete=ReferentialAction.CASCADE)

    ormar_config = ormar.OrmarConfig(
        tablename="quiztivityshares",
        metadata=metadata,
        database=database,
    )


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
    uploaded_at: datetime = ormar.DateTime(nullable=False, default=datetime.now)
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

    ormar_config = ormar.OrmarConfig(
        tablename="storage_items",
        metadata=metadata,
        database=database,
    )


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
    user: uuid.UUID | User = ormar.ForeignKey(User, ondelete=ReferentialAction.CASCADE)
    secret_key: str = ormar.String(nullable=False, max_length=24, min_length=24)
    player_name: str = ormar.Text(nullable=False)
    last_seen: datetime | None = ormar.DateTime(nullable=True)
    first_seen: datetime | None = ormar.DateTime(nullable=True)
    name: str = ormar.Text(nullable=False)
    os_version: str | None = ormar.Text(nullable=True)
    wanted_os_version: str = ormar.Text(nullable=True, default=None)

    ormar_config = ormar.OrmarConfig(
        tablename="controller",
        metadata=metadata,
        database=database,
    )


class Rating(ormar.Model):
    id: uuid.UUID = ormar.UUID(primary_key=True)
    user: uuid.UUID | User = ormar.ForeignKey(User, ondelete=ReferentialAction.CASCADE)
    positive: bool = ormar.Boolean(nullable=False)
    created_at: datetime = ormar.DateTime(nullable=False, server_default=func.now())
    quiz: uuid.UUID | Quiz = ormar.ForeignKey(Quiz, ondelete=ReferentialAction.CASCADE)

    ormar_config = ormar.OrmarConfig(
        tablename="rating",
        metadata=metadata,
        database=database,
    )
