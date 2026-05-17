from fastapi import status

from ..base import BaseErrorWithDetail


class InvalidScopeError(BaseErrorWithDetail):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    def __init__(self, scope: str) -> None:
        self.detail = {"message": f"Invalid jwt scope: {scope}"}
        super().__init__()


class WeakPassword(BaseErrorWithDetail):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = {"message": "Weak password"}


class InvalidPassword(BaseErrorWithDetail):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = {"message": "Incorrect password"}


class InvalidEmailOrPassword(BaseErrorWithDetail):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = {"message": "Incorrect password or email"}


class ExpiredJwtError(BaseErrorWithDetail):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = {"message": "Expired jwt"}


class InvalidTokenError(BaseErrorWithDetail):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = {"message": "Incorrect jwt"}
