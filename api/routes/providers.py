from typing import AsyncGenerator

from fastapi import Depends
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from api.core import connection_store
from api.core.constants import ALGORITHM, SECRET_KEY
from api.core.http_exceptions import credentials_exception, x_not_found_exception
from api.core.security import oauth2_scheme
from api.crud import user_crud
from core.models import User

user_not_found_exception = x_not_found_exception("User")


async def get_session() -> AsyncGenerator:
    async with AsyncSession(
        connection_store.sqla_engine, expire_on_commit=False
    ) as session:
        yield session


async def get_channel() -> AsyncGenerator:
    async with connection_store.rbmq_channel_pool.acquire() as channel:
        yield channel


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_session),
) -> User:

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    db_obj = await user_crud.get_by_username(db, username=username)

    if db_obj is None:
        raise user_not_found_exception

    return db_obj
