# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import enum

from aiohttp import ClientSession
from pydantic import BaseModel


class ImageType(str, enum.Enum):
    all = "all"
    photo = "photo"
    illustration = "illustration"
    vector = "vector"


class Orientation(str, enum.Enum):
    all = ("all",)
    horizontal = "horizontal"
    vertical = "vertical"


class Category(str, enum.Enum):
    background = "background"
    fashion = "fashion"
    nature = "nature"
    science = "science"
    education = "education"
    feelings = "feelings"
    health = "health"
    people = "people"
    religion = "religion"
    places = "places"
    animals = "animals"
    industry = "industry"
    computer = "computer"
    food = "food"
    sports = "sports"
    transportation = "transportation"
    travel = "travel"
    buildings = "buildings"
    business = "business"
    music = "music"


class Colors(str, enum.Enum):
    grayscale = "grayscale"
    transparent = "transparent"
    red = "red"
    orange = "orange"
    yellow = "yellow"
    green = "green"
    turquoise = "turquoise"
    blue = "blue"
    lilac = "lilac"
    pink = "pink"
    white = "white"
    gray = "gray"
    black = "black"
    brown = "brown"


class Order(str, enum.Enum):
    popular = "popular"
    latest = "latest"


class BoolInput(str, enum.Enum):
    true = "true"
    false = "false"


class GetImagesParams(BaseModel):
    q: str = ""
    lang: str = "en"
    id: str = ""
    image_type: ImageType = ImageType.all
    orientation: Orientation = Orientation.all
    category: Category | str = ""
    min_width: int = 0
    min_height: int = 0
    colors: Colors | str = ""
    editors_choice: BoolInput = BoolInput.false
    safesearch: BoolInput = BoolInput.false
    order: Order = Order.popular
    page: int = 1
    pretty: BoolInput = BoolInput.false


class Hit(BaseModel):
    id: int
    pageURL: str
    type: str
    tags: str
    previewURL: str
    previewWidth: int
    previewHeight: int
    webformatURL: str
    webformatWidth: int
    webformatHeight: int
    largeImageURL: str
    imageWidth: int
    imageHeight: int
    imageSize: int
    views: int
    downloads: int
    collections: int
    likes: int
    comments: int
    user_id: int
    user: str
    userImageURL: str


class GetImagesResponse(BaseModel):
    total: int
    totalHits: int
    hits: list[Hit]


class NotFoundError(Exception):
    pass


async def get_images(api_key: str, params: GetImagesParams) -> GetImagesResponse:
    async with (
        ClientSession() as session,
        session.get("https://pixabay.com/api/", params={"key": api_key, **params.dict()}) as resp,
    ):
        if resp.status == 200:
            return GetImagesResponse.parse_obj(await resp.json())
        else:
            raise NotFoundError
