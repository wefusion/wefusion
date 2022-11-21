from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.security import get_password_hash
from api.schemas.user import UserCreate
from core.models import User


class UserCRUD:
    async def get_by_email(
        self, session: AsyncSession, *, email: str
    ) -> Optional[User]:
        result = await session.execute(select(User).where(User.email == email))

        return result.scalars().first()

    async def get_by_username(
        self, session: AsyncSession, *, username: str
    ) -> Optional[User]:
        result = await session.execute(select(User).where(User.username == username))

        return result.scalars().first()

    async def create(self, session: AsyncSession, *, obj_in: UserCreate) -> User:
        password_hash = get_password_hash(obj_in.password)

        user = User(
            username=obj_in.username,
            email=obj_in.email,
            password_hash=password_hash,
            first_name=obj_in.first_name,
            second_name=obj_in.second_name,
        )

        session.add(user)

        await session.commit()
        await session.refresh(user)

        return user
