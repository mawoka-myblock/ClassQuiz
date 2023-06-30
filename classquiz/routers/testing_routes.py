# SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
#
# SPDX-License-Identifier: MPL-2.0


from fastapi import APIRouter
from classquiz.db.models import User
from classquiz.config import settings

settings = settings()

router = APIRouter()


@router.get("/user/{email}")
async def get_user_by_email(email: str, secret_key: str) -> User:
    if secret_key == settings.secret_key:
        return await User.objects.filter(email=email).get()
