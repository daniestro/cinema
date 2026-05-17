from fastapi import status

from .base import BaseErrorWithDetail


class NoAccessError(BaseErrorWithDetail):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = {"message": "No access"}
