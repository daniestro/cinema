from fastapi import status

from ..base import BaseErrorWithDetail


class ProviderRequiresRedirectUrl(BaseErrorWithDetail):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = {"message": "Provider requires redirect url"}


class ProviderExchangeError(BaseErrorWithDetail):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = {"message": "Provider exchange error"}


class ProviderInfoError(BaseErrorWithDetail):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = {"message": "Provider info error"}


class ProviderNotFoundError(BaseErrorWithDetail):
    status_code = status.HTTP_404_NOT_FOUND
    detail = {"message": "Provider not found"}
