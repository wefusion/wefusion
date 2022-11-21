import re
from datetime import timedelta

from fastapi import APIRouter, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.constants import ACCESS_TOKEN_EXPIRE_MINUTES
from api.core.http_exceptions import credentials_exception
from api.core.security import create_access_token, verify_password
from api.crud import user_crud
from api.routes.providers import get_session
from api.schemas.token import Token

auth_router = APIRouter()


def _is_email(sample: str) -> bool:
    # email regex from https://emailregex.com/
    return bool(re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", sample))


@auth_router.post("/oauth2", response_model=Token)
async def oauth2_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    session_obj = await user_crud.get_by_username(session, username=form_data.username)
    if not session_obj:
        raise credentials_exception

    if not verify_password(form_data.password, session_obj.password_hash):
        raise credentials_exception

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": session_obj.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@auth_router.post("/login", response_model=Token)
async def login(
    login: str = Form(),
    password: str = Form(),
    session: AsyncSession = Depends(get_session),
):

    if _is_email(login):
        session_obj = await user_crud.get_by_email(session, email=login)
    else:
        session_obj = await user_crud.get_by_username(session, username=login)

    if not session_obj:
        raise credentials_exception

    if not verify_password(password, session_obj.password_hash):
        raise credentials_exception

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": session_obj.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
