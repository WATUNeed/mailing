from fastapi import HTTPException


class PaginationParameters:
    __slots__ = ('limit', 'offset', '__dict__')

    def __init__(self, limit: int = 10, offset: int = 0):
        if limit < 1 or limit > 10:
            raise HTTPException(
                status_code=422,
                detail='The pagination limit value is incorrect. Should be 1 to 10.'
            )
        if offset < 0:
            raise HTTPException(
                status_code=422,
                detail='The pagination offset value is incorrect. Must be greater than 0.'
            )
        self.limit = limit
        self.offset = offset
