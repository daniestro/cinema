import http
import time
from typing import Optional

from jose import jwt
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer

from core.config import settings


ACCESS_TOKEN_COOKIE = 'access_token'


with open(settings.rsa_public_path, 'r') as _pub:
    _PUBLIC_KEY = _pub.read()


def decode_token(token: str) -> Optional[dict]:
    try:
        decoded_token = jwt.decode(token, _PUBLIC_KEY, algorithms=[settings.jwt_algorithm])
        return decoded_token if decoded_token['exp'] >= time.time() else None
    except Exception:
        return None


def extract_token(request: Request) -> Optional[str]:
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.removeprefix('Bearer ')
    return request.cookies.get(ACCESS_TOKEN_COOKIE)


class JWTBearer(HTTPBearer):
    def __init__(self):
        super().__init__(auto_error=False)

    async def __call__(self, request: Request) -> dict:
        token = extract_token(request)
        if not token:
            raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN, detail='Missing credentials.')
        decoded_token = decode_token(token)
        if not decoded_token:
            raise HTTPException(status_code=http.HTTPStatus.FORBIDDEN, detail='Invalid or expired token.')
        return decoded_token


security_jwt = JWTBearer()
