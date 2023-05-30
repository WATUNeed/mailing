import datetime
import re
import uuid
from typing import Any

from fastapi import HTTPException

from models.db import MessageStates


PHONE_MATCH_PATTERN = re.compile(r'^\d{11}$')
CODE_MATCH_PATTERN = re.compile(r'^\d{3}$')


def validate_id(value: Any) -> uuid.UUID:
    """
    Checks the data type of the variable value.
    :param value:
    :return:
    """
    if not isinstance(value, uuid.UUID):
        raise HTTPException(status_code=422, detail=f'ID should contains only UUID type.')
    return value


def validate_empty(value: Any) -> str:
    """
    Checks the data type of the variable value.
    :param value:
    :return:
    """
    if not value:
        raise HTTPException(status_code=400, detail='Field cannot be empty')
    return value


def validate_phone(value: Any) -> int:
    """
    Checks the phone for validity.
    :param value:
    :return:
    """
    if not re.match(PHONE_MATCH_PATTERN, str(value)):
        raise HTTPException(status_code=422, detail='The number is incorrect')
    return value


def validate_code(value: Any) -> int:
    """
    Checks the code for validity.
    :param value:
    :return:
    """
    if not re.match(CODE_MATCH_PATTERN, str(value)):
        raise HTTPException(status_code=422, detail='The code is incorrect')
    return value


def validate_status(value: Any) -> str:
    """
    Checks the status for validity.
    :param value:
    :return:
    """
    if value not in MessageStates.list():
        raise HTTPException(status_code=422, detail='The status is incorrect')
    return value


def validate_datetime(value: Any) -> datetime.datetime:
    """
    Checks the datetime for validity.
    :param value:
    :return:
    """
    if not isinstance(value, datetime.datetime):
        raise HTTPException(status_code=422, detail='The datetime is incorrect')
    return value
