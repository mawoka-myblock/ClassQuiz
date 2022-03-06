import io

import qrcode
import qrcode.image.svg
from fastapi import APIRouter
from fastapi.responses import Response

from classquiz.config import settings

router = APIRouter()


@router.get("/qr/{quiz_pin}")
async def get_qr(quiz_pin: str):
    """
    Get QR code for quiz
    """
    factory = qrcode.image.svg.SvgImage
    qr = qrcode.QRCode(image_factory=qrcode.image.svg.SvgPathImage, version=1
                       , box_size=20, border=0)
    qr.add_data(f"{settings.root_address}/play?pin={quiz_pin}")
    buf = io.BytesIO()
    qr.make(fit=True)
    qr.make_image(fill_color="black", back_color="white").save(buf, "SVG")
    return Response(content=buf.getvalue(), media_type="image/svg+xml")
