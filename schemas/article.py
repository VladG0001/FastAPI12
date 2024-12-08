from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr, HttpUrl, model_validator, ConfigDict


class InputArticle(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str = Field(min_length=3)
    content: str
    tags: Optional[list[str]] = Field(None)


class InputComment(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    content: str
    article_id: int
    user_id: int


class OutUserName(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str


class SchComment(InputComment):
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime
    author: OutUserName


class SchArticle(InputArticle):
    model_config = ConfigDict(from_attributes=True)

    published_at: datetime
    comments: list[SchComment]
    author: OutUserName


class SchListArticles(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    articles: list[SchArticle] = []
    count: int = 0
