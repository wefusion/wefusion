from fastapi import APIRouter, Depends

from api.routes.providers import get_current_user

from .auth import auth_router
from .execution import execution_router
from .search import search_router
from .user import user_router

api_router = APIRouter()

api_router.include_router(
    execution_router,
    prefix="/exec",
    tags=["Model execution"],
    dependencies=[Depends(get_current_user)],
)

api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Auth"],
)

api_router.include_router(
    user_router,
    prefix="/user",
    tags=["User"],
)

api_router.include_router(
    search_router,
    prefix="/search",
    tags=["Search"],
    dependencies=[Depends(get_current_user)],
)

__all__ = ["api_router"]
