import jwt

from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, Request
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from src.app.core.database import get_db
from src.app.models import User
from src.app.core.config import settings


async def get_user_by_filter(db: AsyncSession, **kwargs) -> User | None:
    result = await db.execute(select(User).filter_by(**kwargs))
    return result.scalar()

async def create_user(db: AsyncSession, email: str, hashed_password: str, name: str) -> User:
    new_user = User(
        email=email,
        name=name, 
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
    
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hash_password: str) -> bool:
    return pwd_context.verify(password, hash_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=45)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm )
    return encoded_jwt


def get_token(request: Request):
    token = request.cookies.get("access_token_blog")
    if not token:
        raise HTTPException(status_code=401)
    return token
    
async def get_current_user(token: str = Depends(get_token), db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.secret_key, settings.algorithm)
    except JWTError:
        raise HTTPException(status_code=401)
    expire: str = payload.get("exp")    
    if (not expire) or (int(expire)<datetime.utcnow().timestamp()):
        raise HTTPException(status_code=401)
    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401)
    user = await get_user_by_filter(db, id=int(user_id))
    if not user:
        raise HTTPException(status_code=401)
    return user