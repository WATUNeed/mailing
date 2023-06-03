import asyncio
import uuid

from celery import Celery

from repository.session import get_session_generator
from services.message import MessageDAL
from settings import settings


celery = Celery('tasks', broker=settings.get_redis_attributes.get('url'))


@celery.task
async def run_mailing(mailing_id: uuid.UUID):
    return await MessageDAL(get_session_generator()).send_messages(mailing_id)
