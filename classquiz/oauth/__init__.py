from fastapi import APIRouter
from classquiz.oauth import google, github


router = APIRouter()
router.include_router(google.router, prefix="/google")
router.include_router(github.router, prefix="/github")
