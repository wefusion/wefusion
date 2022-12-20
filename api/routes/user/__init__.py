from fastapi import APIRouter

from .account import router as account_router
from .comments import router as comments_router
from .history import router as history_router
from .likes import router as likes_router

user_router = APIRouter()

user_router.include_router(history_router, prefix="/history", tags=["History"])
user_router.include_router(likes_router, prefix="/likes", tags=["Likes"])
user_router.include_router(account_router, prefix="/account", tags=["Account"])
user_router.include_router(comments_router, prefix="/comments", tags=["Comments"])

__all__ = ["user_router"]
