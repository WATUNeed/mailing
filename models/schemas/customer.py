import uuid

from pydantic import BaseModel, validator, Field, PositiveInt

from models.schemas.base_shemas import TunedModel
from utils.validation import validate_id, validate_phone, validate_code


# base schemes
class _CustomerWithoutId(BaseModel):
    phone: PositiveInt = Field(default=79270000000)
    code: PositiveInt = Field(default=927)
    time_zone: str

    @validator('phone')
    def validate_phone(cls, value):
        return validate_phone(value)

    @validator('code')
    def validate_code(cls, value):
        return validate_code(value)


class _CustomerFull(_CustomerWithoutId):
    id: uuid.UUID

    @validator('id')
    def validate_id(cls, value):
        return validate_id(value)


# input schemes
class CustomerCreate(_CustomerWithoutId):
    pass


class CustomerEdit(_CustomerFull):
    pass


# output schemes
class ShowCustomer(TunedModel, _CustomerFull):
    pass


class ShowCustomers(TunedModel):
    customers: list[ShowCustomer]
