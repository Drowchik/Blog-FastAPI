from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.database import get_db
from src.app.models import Category, Post
from src.app.schemas.shemas import SCategory


router = APIRouter(
    prefix="/categories",
    tags=["Категория"],
)

@router.get("", response_model=List[SCategory])
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category))
    data = []
    for cat in result.scalars().all():
        data.append(SCategory(
            name=cat.name
        )    
    )
    return data