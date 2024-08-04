from contextlib import asynccontextmanager
from typing import AsyncIterator
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis
from fastapi_pagination import add_pagination

from src.app.resources.user_router import router as user_routers
from src.app.resources.posts_router import router as router_posts
from src.app.resources.categories_router import router as router_category

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield
    
def get_app() -> FastAPI:
    app = FastAPI(title="Blog", description="Author - Denis Sergeev")
    app.include_router(router=router_posts)
    app.include_router(router=user_routers)
    app.include_router(router=router_category)
    app.router.lifespan_context = lifespan
    add_pagination(app)
    return app

