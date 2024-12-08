from typing import Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, model_validator, ConfigDict
import enum

from schemas.article import SchArticle


class UserType(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class InputUserData(BaseModel):
    username: str = Field(min_length=4)
    email: EmailStr
    password: str = Field(min_length=6)
    password_repeat: str = Field(min_length=6)
    role: UserType = UserType.USER

    @model_validator(mode="after")
    @classmethod
    def valid_pass(cls, data: Any):
        if data.password != data.password_repeat:
            raise ValueError("passwords not match")
        return data


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    role: UserType = UserType.USER
    bio: Optional[str] = Field(None)

    create_data: datetime = Field(datetime.now())


class ListBaseUsers(BaseModel):
    users: list[UserBase | None]
    count_users: int


class InputUpdateUser(BaseModel):
    username: Optional[str] = Field(None)
    bio: Optional[str] = None


class OutUserName(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str

class FullUserBase(UserBase):
    model_config = ConfigDict(from_attributes=True)

    articles: SchArticle
