from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.security import get_password_hash, verify_password
from api.crud import user_crud
from api.routes.providers import get_current_user, get_session
from api.schemas.user import UserCreate, UserOut, UserUpdateEmail, UserUpdatePassword
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


@router.put("/password", response_model=UserOut)
async def update_password(
    password_update: UserUpdatePassword,
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(password_update.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password",
        )

    password_hash = get_password_hash(password_update.new_password)

    user = await user_crud.update_password(
        session,
        user=current_user,
        new_password_hash=password_hash,
    )

    return user


@router.put("/email", response_model=UserOut)
async def update_email(
    email_update: UserUpdateEmail,
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(email_update.password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password",
        )

    user = await user_crud.update_email(
        session,
        user=current_user,
        new_email=email_update.email,
    )

    return user
