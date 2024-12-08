from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBasic, HTTPBasicCredentials
from sqlalchemy import select
from starlette import status

from werkzeug.security import check_password_hash

from models import User
from schemas import UserType
from settings import get_session, AsyncSession

route = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


@route.post("/token")
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends(),
                         session: AsyncSession = Depends(get_session)):
    stmt = select(User).filter_by(username=form_data.username)
    user = await session.scalar(stmt)

    if not user or not check_password_hash(user.password_hash, form_data.password):
        raise HTTPException(status_code=400, detail="Username or Password incorrect")

    return {"access_token": user.id, "token_type": "bearer"}


async def get_current_user(token: str = Depends(oauth2_scheme),
                           session: AsyncSession = Depends(get_session)) -> User:
    u_id = token
    stmt = select(User).filter_by(id=u_id)
    user = await session.scalar(stmt)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний токен",
            headers={"Authorization": "Bearer"},
        )
    return user


async def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Only for admin",
            headers={"Authorization": "Bearer"},
        )
    return current_user
