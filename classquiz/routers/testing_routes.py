#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

from fastapi import APIRouter
from classquiz.db.models import User
from classquiz.config import settings

settings = settings()

router = APIRouter()


@router.get("/user/{email}")
async def get_user_by_email(email: str, secret_key: str) -> User:
    if secret_key == settings.secret_key:
        return await User.objects.filter(email=email).get()
