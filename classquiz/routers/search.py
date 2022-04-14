import pydantic
from fastapi import APIRouter

from classquiz.config import settings, meilisearch
from uuid import UUID
from typing import Optional, List

settings = settings()

router = APIRouter()


class Hit(pydantic.BaseModel):
    id: UUID
    title: str
    description: str
    user: str
    formatted: Optional["Hit"] = pydantic.Field(None, alias="_formatted")


class SearchResponse(pydantic.BaseModel):
    hits: List[Hit] | list[None]
    nbHits: int
    exhaustiveNbHits: bool
    query: str
    limit: int
    offset: int
    processingTimeMs: int


class SearchData(pydantic.BaseModel):
    q: str
    offset: Optional[int] = 0
    limit: Optional[int] = 20
    filter: Optional[str] = None
    facetsDistribution: Optional[list[str]] = None
    attributesToRetrieve: Optional[list[str]] = ["*"]
    attributesToCrop: Optional[list[str]] = None
    cropLength: Optional[int] = 200
    attributesToHighlight: Optional[list[str]] = None
    matches: Optional[bool] = False
    sort: Optional[list[str]] = None


@router.post("/", response_model=SearchResponse)
async def search(data: SearchData):
    index = meilisearch.get_index(settings.meilisearch_index)
    query = index.search(
        data.q,
        {
            "offset": data.offset,
            "limit": data.limit,
            "filter": data.filter,
            "cropLength": data.cropLength,
            "matches": data.matches,
            "facetsDistribution": data.facetsDistribution,
            "attributesToRetrieve": data.attributesToRetrieve,
            "attributesToCrop": data.attributesToCrop,
            "sort": data.sort,
            "attributesToHighlight": data.attributesToHighlight,
        },
    )
    return SearchResponse(**query)


@router.get("/", response_model=SearchResponse)
async def search_get(
    q: str,
    offset: int = 0,
    limit: int = 20,
    filter: str | None = None,
    cropLength: int = 200,
    matches: bool = False,
    attributesToHighlight: Optional[str] = "*",
):
    index = meilisearch.get_index(settings.meilisearch_index)
    query = index.search(
        q,
        {
            "offset": offset,
            "limit": limit,
            "filter": filter,  # skipcq: PYL-W0622
            "cropLength": cropLength,
            "matches": matches,
            "attributesToHighlight": [attributesToHighlight],
        },
    )
    return SearchResponse(**query)
