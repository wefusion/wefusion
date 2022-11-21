from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud import user_crud
from api.routes.providers import get_current_user, get_session
from api.schemas.user import UserCreate, UserOut
from core.models import User

router = APIRouter()


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/register", response_model=UserOut)
async def register(
    register_user_in: UserCreate, *, session: AsyncSession = Depends(get_session)
):
    user = await user_crud.get_by_username(session, username=register_user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    user = await user_crud.get_by_email(session, email=register_user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = await user_crud.create(session, obj_in=register_user_in)

    return user
