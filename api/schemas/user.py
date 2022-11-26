from typing import Optional

from pydantic import BaseModel, EmailStr


class BaseUser(BaseModel):
    username: str
    email: EmailStr

    first_name: str
    second_name: Optional[str] = None


class UserCreate(BaseUser):
    password: str


class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str


class UserUpdateEmail(BaseModel):
    new_email: EmailStr
    password: str


class UserOut(BaseUser):
    pass

    class Config:
        orm_mode = True
