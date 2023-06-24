from datetime import datetime
import uuid

from pydantic import BaseModel, validator, Field, PositiveInt

from models.db import MessageStates
from models.schemas.base_shemas import TunedModel
from utils.validation import validate_id, validate_status, validate_datetime, validate_code


# base schemes
class _MessageWithoutId(BaseModel):
    sending_date: datetime
    status: str = Field(default=MessageStates.UNDELIVERED.value)
    mailing_id: uuid.UUID
    customer_id: uuid.UUID

    @validator('sending_date')
    def validate_datetime(cls, value):
        return validate_datetime(value)

    @validator('status')
    def validate_status(cls, value):
        return validate_status(value)

    @validator('mailing_id')
    def validate_mailing_id(cls, value):
        return validate_id(value)

    @validator('customer_id')
    def validate_customer_id(cls, value):
        return validate_id(value)


class _MessageFull(_MessageWithoutId):
    message_id: uuid.UUID

    @validator('message_id')
    def validate_id(cls, value):
        return validate_id(value)


# input schemes
class SendMessages(BaseModel):
    mailing_id: uuid.UUID
    filters: PositiveInt = Field(default=927)

    @validator('mailing_id')
    def validate_id(cls, value):
        return validate_id(value)

    @validator('filters')
    def validate_filters(cls, value):
        return validate_code(value)


class CreateMessage(_MessageWithoutId):
    pass


# output schemes
class ShowMessage(_MessageFull):
    pass


class ShowMessages(TunedModel):
    messages: list[ShowMessage]
