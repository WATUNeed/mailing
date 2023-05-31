import logging

import uvicorn
from fastapi import APIRouter
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from api.routers import customer_router, mailing_router, message_router, statistics_router
from repository.session import create_db_session
from services.mailing import MailingDAL
from settings import settings

from fastapi import FastAPI


app = FastAPI(**settings.get_backend_app_attributes)


@app.on_event("startup")
async def app_startup():
    """
    Setting up the api at start-up.
    :return:
    """

    # logging file setup
    logging.basicConfig(**settings.get_file_logging_attributes)

    # Configuration router
    main_router = APIRouter()
    main_router.include_router(customer_router)
    main_router.include_router(mailing_router)
    main_router.include_router(message_router)
    main_router.include_router(statistics_router)
    app.include_router(main_router)

    # Creating a mailing queue
    session = create_db_session()
    await MailingDAL(db_session=session).run_mailing_queue()

    redis_conn = aioredis.from_url(f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}', encoding='utf8', decode_responses=True)
    FastAPICache.init(RedisBackend(redis_conn), prefix='fastapi-cache')

    logging.info('Application startup complete.')


if __name__ == "__main__":
    uvicorn.run(app=app, **settings.get_uvicorn_app_attributes)
