from typing import NamedTuple
from sqlalchemy.ext.asyncio import AsyncSession


class BaseDAL:
    # base DAL class
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session


class ResponseCode(NamedTuple):
    code: int
    message: str
