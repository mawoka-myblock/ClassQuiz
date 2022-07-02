#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

from fastapi import APIRouter
from classquiz.oauth import google, github


router = APIRouter()
router.include_router(google.router, prefix="/google")
router.include_router(github.router, prefix="/github")
