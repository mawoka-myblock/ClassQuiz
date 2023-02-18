#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
from uuid import UUID

from fastapi import APIRouter, Depends

from classquiz.auth import get_admin_user
from classquiz.db.models import User

router = APIRouter()


@router.delete("/user/id")
async def delete_user_by_id(user_id: UUID, user: User = Depends(get_admin_user)):
    return {"deleted": await User.objects.delete(id=user_id)}


@router.delete("/user/username")
async def delete_user_by_username(username: str, user: User = Depends(get_admin_user)):
    return {"deleted": await User.objects.delete(username=username)}


@router.delete("/user/email")
async def delete_user_by_email(email: str, user: User = Depends(get_admin_user)):
    return {"deleted": await User.objects.delete(email=email)}
