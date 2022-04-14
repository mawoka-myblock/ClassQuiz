import json
import re
import uuid
from datetime import datetime
from random import randint

import pydantic
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from classquiz.auth import get_current_user, get_current_user_optional
from classquiz.config import redis, settings, storage, meilisearch
from uuid import UUID
from typing import Optional, List
from classquiz.db.models import Quiz, QuizInput, User, PlayGame
from classquiz.kahoot_importer.import_quiz import import_quiz

settings = settings()

router = APIRouter()


class Hit(pydantic.BaseModel):
    id: UUID
    title: str
    description: str
    user: str
    formatted: Optional['Hit'] = pydantic.Field(None, alias='_formatted')


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
    attributesToCrop: Optional[list[str]]= None
    cropLength: Optional[int] = 200
    attributesToHighlight: Optional[list[str]] = None
    matches: Optional[bool] = False
    sort: Optional[list[str]] = None


@router.post("/search", response_model=SearchResponse)
async def search(data: SearchData):
    index = meilisearch.get_index(settings.meilisearch_index)
    query = index.search(data.q, {
        "offset": data.offset,
        "limit": data.limit,
        "filter": data.filter,
        "cropLength": data.cropLength,
        "matches": data.matches,
        "facetsDistribution": data.facetsDistribution,
        "attributesToRetrieve": data.attributesToRetrieve,
        "attributesToCrop": data.attributesToCrop,
        "sort": data.sort,
        "attributesToHighlight": data.attributesToHighlight
    })
    return query.serialize()


@router.get("/search", response_model=SearchResponse)
async def search_get(q: str, offset: int = 0, limit: int = 20, filter: str | None = None,
                     cropLength: int = 200, matches: bool = False, attributesToHighlight: Optional[str] = "*"):
    index = meilisearch.get_index(settings.meilisearch_index)
    query = index.search(q, {
        "offset": offset,
        "limit": limit,
        "filter": filter,
        "cropLength": cropLength,
        "matches": matches,
        "attributesToHighlight": [attributesToHighlight]
    })
    return SearchResponse(**query)
