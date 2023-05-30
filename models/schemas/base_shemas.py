from pydantic import BaseModel


class TunedModel(BaseModel):
    """
    The basic model for output schemes.
    """
    class Config:
        orm_mode = True
