from typing import Any

from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound, IntegrityError


def catch_exceptions(func: Any) -> Any:
    """
    Decorator for accessing the database. Traps SQL errors.
    :param func:
    :return: Callable func
    """
    async def wrapped(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except NoResultFound:
            raise HTTPException(status_code=404, detail='No entry found')
        except IntegrityError:
            raise HTTPException(status_code=403, detail='Already taken')
    return wrapped


def services_request(func: Any) -> Any:
    async def wrapped(self, *args, **kwargs) -> Any:
        async with self.db_session as session:
            self.db_session = session
            return await func(self, *args, **kwargs)

    return wrapped
