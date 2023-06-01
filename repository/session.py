from typing import Generator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager

from settings import settings


def create_db_session() -> AsyncSession:
    """
    Creates a session.
    :return:
    """
    engine = create_async_engine(settings.get_db_url, future=True, echo=False)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    return async_session()


@asynccontextmanager
async def get_session_generator() -> Generator[AsyncSession, None, None]:
    """
    Connects to the database.
    :return: Session.
    """
    session: AsyncSession = None
    try:
        session = create_db_session()
        yield session
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.commit()
        await session.close()
