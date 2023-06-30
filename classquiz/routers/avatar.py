# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import gzip

from fastapi import APIRouter, Response, HTTPException, Depends
import py_avataaars_no_png as av
from fastapi.responses import PlainTextResponse
from classquiz.config import redis

from classquiz.auth import get_current_user
from classquiz.db.models import User

router = APIRouter()


class AvatarItemsAsList:
    skin_color = list(av.SkinColor)
    hair_color = list(av.HairColor)
    facial_hair_type = list(av.FacialHairType)
    facial_hair_color = list(av.HairColor)
    top_type = list(av.TopType)
    hat_color = list(av.Color)
    mouth_type = list(av.MouthType)
    eyebrow_type = list(av.EyebrowType)
    nose_type = list(av.NoseType)
    accessories_type = list(av.AccessoriesType)
    clothe_type = list(av.ClotheType)
    clothe_color = list(av.Color)
    clothe_graphic_type = list(av.ClotheGraphicType)


@router.get("/custom", response_class=PlainTextResponse)
async def get_customized_avatar(
    resp: Response,
    skin_color: int | None = 0,
    hair_color: int | None = 0,
    facial_hair_type: int | None = 0,
    facial_hair_color: int | None = 0,
    top_type: int | None = 0,
    hat_color: int | None = 0,
    mouth_type: int | None = 0,
    eyebrow_type: int | None = 0,
    nose_type: int | None = 0,
    accessories_type: int | None = 0,
    clothe_type: int | None = 0,
    clothe_color: int | None = 0,
    clothe_graphic_type: int | None = 0,
):
    try:
        skin_color = AvatarItemsAsList.skin_color[skin_color]
        hair_color = AvatarItemsAsList.hat_color[hair_color]
        facial_hair_type = AvatarItemsAsList.facial_hair_type[facial_hair_type]
        facial_hair_color = AvatarItemsAsList.facial_hair_color[facial_hair_color]
        top_type = AvatarItemsAsList.top_type[top_type]
        hat_color = AvatarItemsAsList.hat_color[hat_color]
        mouth_type = AvatarItemsAsList.mouth_type[mouth_type]
        eyebrow_type = AvatarItemsAsList.eyebrow_type[eyebrow_type]
        nose_type = AvatarItemsAsList.nose_type[nose_type]
        accessories_type = AvatarItemsAsList.accessories_type[accessories_type]
        clothe_type = AvatarItemsAsList.clothe_type[clothe_type]
        clothe_color = AvatarItemsAsList.clothe_color[clothe_color]
        clothe_graphic_type = AvatarItemsAsList.clothe_graphic_type[clothe_graphic_type]
    except IndexError:
        raise HTTPException(status_code=400, detail="One parameter-value doesn't exist.")
    resp.headers.append("Content-Type", "image/svg+xml")
    avatar = av.PyAvataaar(
        style=av.AvatarStyle.TRANSPARENT,
        skin_color=skin_color,
        hair_color=hair_color,
        facial_hair_type=facial_hair_type,
        facial_hair_color=facial_hair_color,
        top_type=top_type,
        hat_color=hat_color,
        mouth_type=mouth_type,
        eyebrow_type=eyebrow_type,
        nose_type=nose_type,
        accessories_type=accessories_type,
        clothe_type=clothe_type,
        clothe_color=clothe_color,
        clothe_graphic_type=clothe_graphic_type,
    ).render_svg()
    # skipcq: PY-W0069
    # print(f"skin_color: {len(AvatarItemsAsList.skin_color)},")
    # print(f"hair_color: {len(AvatarItemsAsList.hair_color)},")
    # print(f"facial_hair_type: {len(AvatarItemsAsList.facial_hair_type)},")
    # print(f"facial_hair_color: {len(AvatarItemsAsList.facial_hair_color)},")
    # print(f"top_type: {len(AvatarItemsAsList.top_type)},")
    # print(f"hat_color: {len(AvatarItemsAsList.hat_color)},")
    # print(f"mouth_type: {len(AvatarItemsAsList.mouth_type)},")
    # print(f"eyebrow_type: {len(AvatarItemsAsList.eyebrow_type)},")
    # print(f"nose_type: {len(AvatarItemsAsList.nose_type)},")
    # print(f"accessories_type: {len(AvatarItemsAsList.accessories_type)},")
    # print(f"clothe_type: {len(AvatarItemsAsList.clothe_type)},")
    # print(f"clothe_color: {len(AvatarItemsAsList.clothe_color)},")
    # print(f"clothe_graphic_type: {len(AvatarItemsAsList.clothe_graphic_type)},")
    return avatar


@router.post("/save")
async def save_avatar(
    skin_color: int | None = 0,
    hair_color: int | None = 0,
    facial_hair_type: int | None = 0,
    facial_hair_color: int | None = 0,
    top_type: int | None = 0,
    hat_color: int | None = 0,
    mouth_type: int | None = 0,
    eyebrow_type: int | None = 0,
    nose_type: int | None = 0,
    accessories_type: int | None = 0,
    clothe_type: int | None = 0,
    clothe_color: int | None = 0,
    clothe_graphic_type: int | None = 0,
    user: User = Depends(get_current_user),
):
    try:
        skin_color = AvatarItemsAsList.skin_color[skin_color]
        hair_color = AvatarItemsAsList.hat_color[hair_color]
        facial_hair_type = AvatarItemsAsList.facial_hair_type[facial_hair_type]
        facial_hair_color = AvatarItemsAsList.facial_hair_color[facial_hair_color]
        top_type = AvatarItemsAsList.top_type[top_type]
        hat_color = AvatarItemsAsList.hat_color[hat_color]
        mouth_type = AvatarItemsAsList.mouth_type[mouth_type]
        eyebrow_type = AvatarItemsAsList.eyebrow_type[eyebrow_type]
        nose_type = AvatarItemsAsList.nose_type[nose_type]
        accessories_type = AvatarItemsAsList.accessories_type[accessories_type]
        clothe_type = AvatarItemsAsList.clothe_type[clothe_type]
        clothe_color = AvatarItemsAsList.clothe_color[clothe_color]
        clothe_graphic_type = AvatarItemsAsList.clothe_graphic_type[clothe_graphic_type]
    except IndexError:
        raise HTTPException(status_code=400, detail="One parameter-value doesn't exist.")
    avatar = av.PyAvataaar(
        style=av.AvatarStyle.TRANSPARENT,
        skin_color=skin_color,
        hair_color=hair_color,
        facial_hair_type=facial_hair_type,
        facial_hair_color=facial_hair_color,
        top_type=top_type,
        hat_color=hat_color,
        mouth_type=mouth_type,
        eyebrow_type=eyebrow_type,
        nose_type=nose_type,
        accessories_type=accessories_type,
        clothe_type=clothe_type,
        clothe_color=clothe_color,
        clothe_graphic_type=clothe_graphic_type,
    ).render_svg()
    user.avatar = gzip.compress(str.encode(avatar))
    await redis.delete(user.email)
    await user.update()
