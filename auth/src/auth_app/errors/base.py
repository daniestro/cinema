from typing import Any


class BaseError(Exception):
    ...


class BaseErrorWithDetail(BaseError):
    status_code: int
    detail: dict[str, Any]
