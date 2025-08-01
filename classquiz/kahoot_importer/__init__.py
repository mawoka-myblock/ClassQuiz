# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


from typing import List, Any, Optional
from uuid import UUID

from pydantic import BaseModel


class _CoverMetadata(BaseModel):
    id: UUID | None = None
    resources: str | None = None


class _CreatorAvatar(BaseModel):
    url: str | None = None
    id: UUID | None = None
    type: str | None = None
    bitmojiAvatarId: str | None = None
    altText: str | None = None
    contentType: str | None = None
    width: int | None = None
    height: int | None = None


class _LastEdit(BaseModel):
    editorUserId: UUID
    editorUsername: str
    editTimestamp: int


class _ImageMetadata(BaseModel):
    id: UUID | None = None
    content_type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    resources: Optional[str] = None


class _SampleQuestion(BaseModel):
    image: str | None = None
    imageMetadata: _ImageMetadata | None = None
    title: str
    type: str
    time: int | None = None


class _Access(BaseModel):
    groupRead: List[Any | None]
    folderGroupIds: List[Any | None]


class _Card(BaseModel):
    type: str
    title: str
    description: str
    slug: str
    cover: str | None = None
    coverMetadata: _CoverMetadata | dict[None, None] | None = None
    draftExists: bool
    inventoryItemIds: List[Any] = None
    number_of_questions: int
    creator: UUID
    creator_username: str
    creator_avatar: _CreatorAvatar | dict[None, None] | None = None
    badges: List[str]
    visibility: int
    locked: bool
    writeProtection: bool
    lastEdit: _LastEdit | None = None
    featured: bool
    young_featured: bool
    sponsored: bool
    draft: bool
    combined: bool
    compatibility_level: int
    sample_questions: List[_SampleQuestion]
    number_of_plays: int
    number_of_players: int
    total_favourites: int
    question_types: List[str]
    created: int
    modified: int
    access: _Access
    duplication_disabled: bool
    uuid: UUID


class _Entity(BaseModel):
    card: _Card


class _Origin(BaseModel):
    x: int
    y: int


class _Crop(BaseModel):
    origin: _Origin
    target: _Origin
    circular: bool


class _LanguageInfo(BaseModel):
    language: str
    lastUpdatedOn: int
    readAloudSupported: bool


class _Metadata(BaseModel):
    access: _Access
    duplicationProtection: bool | None = None
    lastEdit: _LastEdit | None = None


class _Parent(BaseModel):
    id: UUID
    creator_username: str


class _Choice(BaseModel):
    answer: str
    correct: bool
    languageInfo: _LanguageInfo | None = None


class _Video(BaseModel):
    startTime: float
    endTime: float
    service: str
    full_url: Optional[str] = None
    id: Optional[str] = None


class _Question(BaseModel):
    type: str
    question: str
    time: int
    points: bool
    pointsMultiplier: int
    choices: List[_Choice]
    image: str | None = None
    imageMetadata: _ImageMetadata | None = None
    resources: Optional[str] = None
    video: _Video
    questionFormat: int
    languageInfo: _LanguageInfo | None = None
    media: List[Any]


class _Kahoot(BaseModel):
    uuid: UUID
    language: str
    creator: UUID
    creator_username: str
    compatibilityLevel: int
    creator_primary_usage: str
    folderId: UUID | None = None
    visibility: int
    difficulty: int | None = None
    audience: str
    audience: str
    title: str
    description: str
    quizType: str
    tags: str | None | List[str] = None
    cover: str | None = None
    coverMetadata: _CoverMetadata | dict[None, None] | None = None
    questions: List[_Question]
    metadata: _Metadata
    parent: _Parent | None = None
    resources: str | None = None
    slug: str
    languageInfo: _LanguageInfo | None = None
    inventoryItemIds: List[Any]
    type: str
    created: int
    modified: int
