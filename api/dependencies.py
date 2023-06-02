from typing import NamedTuple


class Paginator(NamedTuple):
    limit: int
    offset: int

    def __call__(self):
        return self


def get_paginator_params(limit: int = 10, offset: int = 0) -> Paginator:
    return Paginator(limit=limit, offset=offset)
