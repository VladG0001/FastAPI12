from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from models import Article, User
from schemas import InputArticle, SchArticle, SchListArticles
from settings import settings_app as s
from settings import get_session
from routes.user import get_current_user
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import session
from starlette import status
from sqlalchemy import select, or_, and_, func
from models import Comment, User, Article
from routes.auth import get_current_user
from schemas import InputComment
from settings import settings_app as s
from settings import get_session

route = APIRouter()


@route.post("/")
async def create_article(article: InputArticle,
                         user=Depends(get_current_user),
                         session=Depends(get_session)) -> SchArticle:
    new_article = Article(**article.model_dump(), author=user)
    session.add(new_article)
    try:
        await session.commit()
        await session.refresh(new_article)
        return SchArticle.model_validate(new_article)

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Помилка при створенні статті")


@route.get("/{article_id}")
async def get_article_by_id(article_id: int,
                            session: AsyncSession = Depends(get_session)) -> SchArticle:
    article = await session.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Стаття не знайдена.")
    return SchArticle.model_validate(article)


@route.get('/get/all')
async def all_articles(
        page_num: int = Query(1),
        item: int = Query(2),
        session: AsyncSession = Depends(get_session)
):
    total_count = await session.scalar(select(func.count()).select_from(Article))
    stmt = (select(Article)
            .order_by(Article.published_at.desc())
            .offset((page_num - 1) * item)
            .limit(item))

    articles = await session.scalars(stmt)
    articles = articles.all()
    if not articles:
        raise HTTPException(status_code=404, detail="Статті відсутні.")
    return SchListArticles(articles=articles, count=total_count)


@route.put('/{article_id}')
async def change_article(article_id: int,
                         article_data: InputArticle,
                         _=Depends(get_current_user),
                         session: AsyncSession = Depends(get_session)):
    article = await session.get(Article, article_id)

    article.title = article_data.title
    article.content = article_data.content
    article.tags = article_data.tags

    await session.commit()
    await session.refresh(article)
    return SchArticle.model_validate(article)


@route.delete('/{article_id}')
async def delete_article_by_id(article_id: int,
                               session: AsyncSession = Depends(get_session),
                               _=Depends(get_current_user)):
    article = await session.get(Article, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    await session.delete(article)
    await session.commit()
    return {"message": f"{article_id} delete successfully"}


@route.post("/create_comment/")
async def create_comment(content: str, article_id: int,
                         current_user: User = Depends(get_current_user),
                         session: AsyncSession = Depends(get_session)
                         ):
    stmt = select(Article).filter(Article.id == article_id)
    article = await session.scalar(stmt)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    new_comment = Comment(content=content, user_id=current_user.id, article_id=article_id)
    session.add(new_comment)
    await session.commit()
    await session.refresh(new_comment)
    return InputComment.model_validate(new_comment)


@route.delete("/delete_comment/")
async def delete_comment(comment_id: int,
                         _: User = Depends(get_current_user),
                         session: AsyncSession = Depends(get_session)
                         ):
    result = await session.execute(select(Comment).filter(Comment.id == comment_id))
    comment = result.scalars().first()

    if comment:
        await session.delete(comment)
        await session.commit()
        return f"Comment {comment_id} успішно видалений."
    else:
        raise ValueError(f"Comment {comment_id} незнайдено.")


@route.get("/content/search/")
async def search(query: str | None = Query(None, description="str for search"),
                 session: AsyncSession = Depends(get_session)):
    stmt = (select(Article)
            .filter(or_(Article.title.ilike(f"%{query}%"), Article.content.ilike(f"%{query}%")))
            .order_by(Article.published_at.desc()))

    res = await session.scalars(stmt)
    articles = res.all()
    return SchListArticles(articles=articles, count=len(articles))


@route.get("/search/get/")
async def search(query: str = Query(..., description="search by title and content"),
                 start_date: date = Query(None, description="Start date for published articles"),
                 end_date: date = Query(None, description="End date for published articles"),
                 session: AsyncSession = Depends(get_session)) -> SchListArticles:
    # # full search
    # stmt = (
    #     select(Article)
    #     .filter(or_(Article.title.ilike(f"%{query}%"), Article.content.ilike(f"%{query}%"))
    #     .order_by(Article.published_at.desc()))
    # )

    stmt = (
        select(Article)
        .filter(or_(Article.title.ilike(f"%{query}%"), Article.content.ilike(f"%{query}%")))
    )
    if start_date and end_date:
        stmt = stmt.filter(
            and_(
                Article.published_at >= start_date,
                Article.published_at <= end_date
            )
        )
    elif start_date:
        stmt = stmt.filter(Article.published_at >= start_date)
    elif end_date:
        stmt = stmt.filter(Article.published_at <= end_date)

    stmt = stmt.order_by(Article.published_at.desc())

    result = await session.scalars(stmt)
    articles = result.all()

    return SchListArticles(articles=articles, count=len(articles))
