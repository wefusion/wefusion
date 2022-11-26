from fastapi import APIRouter

from .account import router as account_router
from .gallery import router as gallery_router

user_router = APIRouter()

user_router.include_router(gallery_router, prefix="/gallery", tags=["Gallery"])
user_router.include_router(account_router, prefix="/account", tags=["Account"])

__all__ = ["user_router"]
