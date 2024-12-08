import asyncio

from werkzeug.security import generate_password_hash

from settings import Base, async_session, engine
from schemas import UserType
from models import Article, Comment, User


async def create_bd():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def insert_data():
    async with async_session() as sess:
        u1 = User(username="admin",
                  email="admin@ex.com",
                  password_hash=generate_password_hash("admin"),
                  role=UserType.ADMIN,
                  bio="Master admin",
                  )
        u2 = User(username="user",
                  email="user@ex.com",
                  password_hash=generate_password_hash("user"),
                  role=UserType.USER,
                  bio="just user",
                  )

        art1 = Article(title="Error handling", content="""Pydantic will raise a ValidationError exception whenever it finds an error in the data it's validating.
A single exception will be raised regardless of the number of errors found, and that validation error will contain information about all of the errors and how they happened.
See Error Handling for details on standard and custom errors.""", tags=["python", "error"], author=u1)

        art2 = Article(title="Note", content="""I need to buy bread""", tags=["note"], author=u2)

        comm1 = Comment(content="cool article", author=u2, article=art1)
        comm2 = Comment(content="yep is cool", author=u1, article=art1)
        sess.add_all([u1, u2, art1, art2, comm1, comm2])
        await sess.commit()


async def main():
    await create_bd()
    print("database created")
    await insert_data()
    print("data added")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
