from fastapi import status

from .base import BaseErrorWithDetail


class UserNotFound(BaseErrorWithDetail):
    status_code = status.HTTP_404_NOT_FOUND
    detail = {"message": "User not found"}


class InvalidEmail(BaseErrorWithDetail):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = {"message": "Invalid email"}


class AlreadyTakenEmail(BaseErrorWithDetail):
    status_code = status.HTTP_409_CONFLICT
    detail = {"message": "Already taken email"}


class UserAlreadyHasRole(BaseErrorWithDetail):
    status_code = status.HTTP_409_CONFLICT
    detail = {"message": "Already taken role"}


class UserDoesNotHaveRole(BaseErrorWithDetail):
    status_code = status.HTTP_404_NOT_FOUND
    detail = {"message": "User does not have role"}


class RoleNotFound(BaseErrorWithDetail):
    status_code = status.HTTP_404_NOT_FOUND
    detail = {"message": "Role not found"}


class RoleAlreadyExists(BaseErrorWithDetail):
    status_code = status.HTTP_409_CONFLICT
    detail = {"message": "Already existing role"}


class AlreadyExistingSocialNet(BaseErrorWithDetail):
    status_code = status.HTTP_409_CONFLICT
    detail = {"message": "Already social net"}


class SocialnetNotFound(BaseErrorWithDetail):
    status_code = status.HTTP_404_NOT_FOUND
    detail = {"message": "Social net not found"}


class UserNotHaveSocialNet(BaseErrorWithDetail):
    status_code = status.HTTP_404_NOT_FOUND
    detail = {"message": "User doest not have social net"}
