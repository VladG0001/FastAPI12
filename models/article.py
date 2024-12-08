from sqlalchemy import JSON, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from models.user import User

from settings import Base


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    content: Mapped[str] = mapped_column(nullable=False, index=True)
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=True)

    published_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    author: Mapped[User] = relationship(back_populates='articles', lazy="selectin")

    comments: Mapped[list['Comment']] = relationship(
        back_populates='article',
        cascade="all, delete-orphan",
        lazy="selectin")

    def __str__(self):
        return f"Article : {self.title}, {self.author.username}"


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    author: Mapped[User] = relationship(back_populates='comments', lazy="selectin")

    article_id: Mapped[int] = mapped_column(ForeignKey('articles.id'))
    article: Mapped['Article'] = relationship(back_populates='comments', lazy="selectin")

    def __str__(self):
        return f"comment : {self.content}, {self.author.username}"
