from datetime import datetime
import uuid

from pydantic import BaseModel, validator, Field, PositiveInt

from models.schemas.base_shemas import TunedModel
from models.schemas.message import ShowMessages
from utils.validation import validate_id, validate_datetime, validate_code


# base schemes
class _MailingWithoutId(BaseModel):
    start_date: datetime
    message: str = Field(default='Hello, World!')
    filters: PositiveInt = Field(default=927)
    expiry_date: datetime

    @validator('start_date')
    def validate_start_date(cls, value):
        return validate_datetime(value)

    @validator('filters')
    def validate_filters(cls, value):
        return validate_code(value)

    @validator('expiry_date')
    def validate_expiry_date(cls, value):
        return validate_datetime(value)


class _MailingFull(_MailingWithoutId):
    mailing_id: uuid.UUID

    @validator('mailing_id')
    def validate_id(cls, value):
        return validate_id(value)


# input schemes
class MailingCreate(_MailingWithoutId):
    pass


class MailingEdit(_MailingFull):
    pass


# output schemes
class ShowMailing(TunedModel, _MailingFull):
    pass


class ShowStatisticsByMailing(ShowMailing):
    delivered_count: int
    undelivered_count: int
    delivered_messages: ShowMessages = []
    undelivered_messages: ShowMessages = []


class ShowStatisticsMailings(TunedModel):
    completed_mailings_count: int
    uncompleted_mailings_count: int
    total_delivered_messages: int
    total_undelivered_messages: int
    mailings: list[ShowStatisticsByMailing] = []


class ShowMailingAPIResponse(TunedModel):
    code: PositiveInt = Field(default=200)
    message: str

    @validator('code')
    def validate_code(cls, value):
        return validate_code(value)
