import asyncio

from datetime import datetime
from typing import List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi_cache.decorator import cache
from fastapi_pagination import LimitOffsetPage, add_pagination, Params
from fastapi_pagination.ext.sqlalchemy import paginate

from src.app.core.database import get_db
from src.app.models import Post, User
from src.app.schemas.shemas import SPostBase, SPostCreate, SPostResponse
from src.app.services.auth import get_current_user
from src.app.services.elasticsearch import es

router = APIRouter(
    prefix="/posts",
    tags=["Посты"],
)



@router.get("/my", response_model=LimitOffsetPage)
async def get_my_posts(user: User = Depends(get_current_user),
                       db: AsyncSession = Depends(get_db),
                       params: Params = Depends()):
    try:
        paginated_result = await paginate(db, select(Post).filter(Post.user_id == user.id).options(selectinload(Post.category)), params)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Erorr:  {e}")
    response = []
    for post in paginated_result.items:
        response.append(SPostResponse(
            title=post.title,
            description=post.description,
            username=post.user.name,
            category_name=post.category.name
        ))
    return LimitOffsetPage.create(items=response, total=paginated_result.total, params=params)

@router.post("")
async def add_post(post: SPostCreate,  user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        new_post = Post(title=post.title, description=post.description, category_id=post.category_id, user_id=user.id, updated_at=datetime.utcnow())
        db.add(new_post)
        await db.commit()
        await db.refresh(new_post)
        await es.index_post(new_post)
        return new_post
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Что-то пошло не так, пост не добавлен, ошибка {e}")
    
@router.get("", response_model=LimitOffsetPage)
@cache(expire=20)
async def get_posts(category_ids: List[int] = Query(None),
                    db: AsyncSession = Depends(get_db),
                    params: Params = Depends()):
    try:
        query = select(Post).options(selectinload(Post.category), selectinload(Post.user))
        if category_ids:
            query=query.filter(Post.category_id.in_(category_ids))
        result = await paginate(db, query, params)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"sds {e}")
    response = []
    for post in result.items:
        response.append(SPostResponse(
            title=post.title,
            description=post.description,
            username=post.user.name,
            category_name=post.category.name
        ))
    return LimitOffsetPage.create(items=response, total=result.total, params=params)

@router.get("/search")
async def search_post_get(query: str):
    try:
        result = await es.search_post(query)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Mistake {e}")
    
@router.get("/{post_id}", response_model=SPostResponse)
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute((select(Post).filter(Post.id==post_id)).options(selectinload(Post.category), selectinload(Post.user)))
        post=result.scalars().first()
        if not post:
            raise HTTPException(status_code=404, detail="Пост не найден")
        response = SPostResponse(
            title=post.title,
            description=post.description,
            username=post.user.name,
            category_name=post.category.name
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла ошибка, попробуйте позже, ошибка {e}")
    
@router.delete("/{post_id}")
async def delete_post(post_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Post).filter(Post.id==post_id))
        post = result.scalars().first()
        if not post:
            raise HTTPException(status_code=404, detail="Пост не был найден, он не существует")
        if post.user_id != user.id or user.is_superuser:
            raise HTTPException(status_code=403, detail="У вас нет прав для удаления этого поста")
        await db.delete(post)
        await db.commit()
        return "Успешно удалено"
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Произошла ошибка при удалении поста. Повторить позже {e}")

@router.patch("")
async def edit_post(post_id: int, post_update: SPostBase, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Post).filter(Post.id==post_id))
        post = result.scalars().first()
        if not post:
            raise HTTPException(status_code=404, detail="Пост не был найден, он не существует")
        if post.user_id != user.id:
            raise HTTPException(status_code=403, detail="У вас нет прав для изменения этого поста")
        post.description = post_update.description
        post.title = post_update.title
        await db.commit()
        await db.refresh(post)
        await es.index_post(post)
        return "Успешно обновлено"
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Произошла ошибка при удалении поста. Повторить позже {e}")
