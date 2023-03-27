#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

from fastapi import APIRouter
from classquiz.routers.box_controller import web, embedded

router = APIRouter()

router.include_router(web.router, prefix="/web")
router.include_router(embedded.router, prefix="/embedded")
