import logging

import uvicorn
from fastapi import APIRouter
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from starlette.middleware.cors import CORSMiddleware

from api.routers import customer_router, mailing_router, message_router, statistics_router
from repository.session import create_db_session
from services.mailing import MailingDAL
from settings import settings

from fastapi import FastAPI

from utils.logger_config import configurate_logging_file


app = FastAPI(**settings.get_backend_app_attributes)
app.add_middleware(CORSMiddleware, **settings.get_middleware_attributes)


@app.on_event("startup")
async def app_startup():
    """
    Setting up the api at start-up.
    :return:
    """

    # Configure logging
    configurate_logging_file()

    # Configuration router
    main_router = APIRouter()
    main_router.include_router(customer_router)
    main_router.include_router(mailing_router)
    main_router.include_router(message_router)
    main_router.include_router(statistics_router)
    app.include_router(main_router)

    # Configuration redis
    redis_conn = aioredis.from_url(**settings.get_redis_attributes)
    FastAPICache.init(RedisBackend(redis_conn), prefix='fastapi-cache')

    logging.info('Application startup complete.')


if __name__ == "__main__":
    uvicorn.run(app=app, **settings.get_uvicorn_attributes)
