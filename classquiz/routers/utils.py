# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


import io

import qrcode
import qrcode.image.svg
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from pydantic import BaseModel, Field, ValidationError
from fastapi.responses import JSONResponse

from classquiz.auth import get_current_user
from classquiz.config import settings
from aiohttp import ClientSession

from classquiz.db.models import User

settings = settings()

router = APIRouter()


@router.get("/qr/{quiz_pin}")
async def get_qr(quiz_pin: str, dark_mode: bool = False):
    """
    Get QR code for quiz
    """
    qr = qrcode.QRCode(image_factory=qrcode.image.svg.SvgPathImage, version=1, box_size=20, border=0)
    qr.add_data(f"{settings.root_address}/play?pin={quiz_pin}&ref=Qr")
    buf = io.BytesIO()
    qr.make(fit=True)
    qr.make_image(fill_color="black", back_color="white").save(buf, "SVG")
    data = buf.getvalue()
    if dark_mode:
        data = data.replace(b'fill="#000000"', b'fill="#ffffff"')
    return Response(content=data, media_type="image/svg+xml")


class IpResponse(BaseModel):
    status: str
    country: str
    countryCode: str
    region: str
    regionName: str
    city: str
    zip: str
    lat: float
    lon: float
    timezone: str
    isp: str
    org: str
    as_attr: str = Field(alias="as")
    query: str


@router.get("/ip-lookup/{ip}", response_model=IpResponse)
async def get_ip_data(ip: str, _: User = Depends(get_current_user)):
    async with ClientSession() as session, session.get(f"http://ip-api.com/json/{ip}") as response:
        data = await response.json()
        try:
            return IpResponse(**data)
        except ValidationError:
            return JSONResponse(status_code=response.status, content=data)
