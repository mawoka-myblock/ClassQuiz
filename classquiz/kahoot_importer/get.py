from uuid import UUID
from typing import List, Any, Optional
from aiohttp import ClientSession

from pydantic import BaseModel


class _Access(BaseModel):
    groupRead: List[Any | None]
    folderGroupIds: List[Any | None]


class _CoverMetadata(BaseModel):
    id: UUID
    resources: str | None


class _CreatorAvatar(BaseModel):
    url: str
    id: UUID | None
    type: str | None
    bitmojiAvatarId: str | None
    altText: str | None
    contentType: str | None
    width: int | None
    height: int | None


class _LastEdit(BaseModel):
    editorUserId: UUID
    editorUsername: str
    editTimestamp: int


class _ImageMetadata(BaseModel):
    id: UUID
    content_type: Optional[str]
    width: Optional[int]
    height: Optional[int]
    resources: Optional[str]


class _SampleQuestion(BaseModel):
    image: str | None
    imageMetadata: _ImageMetadata | None
    title: str
    type: str
    time: int


class _Card(BaseModel):
    type: str
    title: str
    description: str
    slug: str
    cover: str | None
    coverMetadata: _CoverMetadata | dict[None, None]
    draftExists: bool
    inventoryItemIds: List[Any]
    number_of_questions: int
    creator: UUID
    creator_username: str
    creator_avatar: _CreatorAvatar | dict[None, None] | None
    badges: List[str]
    visibility: int
    locked: bool
    writeProtection: bool
    last_edit: _LastEdit | None
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


class _Response(BaseModel):
    entities: List[_Entity]
    totalHits: int
    cursor: int
    pageTimestamp: int


async def get(query: str | None, limit: int | None = 9, cursor: int | None = 1,
              search_cluster: int | None = 1, inventory_item_id: str | None = "ANY") -> _Response:
    """

    :param inventory_item_id: I dkon't know
    :param search_cluster: Doesn't seeem to matter
    :param cursor: The position in the result-list (page)
    :param query: The search query
    :param limit: Less or equals 100
    :return:
    """
    async with ClientSession() as session:
        async with session.get(
                f"https://create.kahoot.it/rest/kahoots/?query={query}&limit={limit}&cursor={cursor}&searchCluster={search_cluster}&includeExtendedCounters=false&inventoryItemId={inventory_item_id}"

        ) as response:
            print(
                f"https://create.kahoot.it/rest/kahoots/?query={query}&limit={limit}&cursor={cursor}&searchCluster={search_cluster}&includeExtendedCounters=false&inventoryItemId={inventory_item_id}")
            return _Response(**await response.json())
