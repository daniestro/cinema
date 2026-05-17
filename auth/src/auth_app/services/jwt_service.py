import uuid
from datetime import datetime, timedelta
from functools import lru_cache

import jwt

from auth_app.core.config import settings as s
from auth_app.errors.services import ExpiredJwtError, InvalidScopeError, InvalidTokenError

from .misc import Scope


class JWTService:
    def __init__(
        self,
        private_key: str,
        public_key: str,
        access_token_lifetime: timedelta,
        refresh_token_lifetime: timedelta,
    ) -> None:
        self.private_key = private_key
        self.public_key = public_key
        self.access_token_lifetime = access_token_lifetime
        self.refresh_token_lifetime = refresh_token_lifetime

    def encode_access_token(self, user_id: str, email: str, roles: list[str]) -> str:
        payload = {
            "exp": datetime.utcnow() + self.access_token_lifetime,
            "iat": datetime.utcnow(),
            "scope": Scope.ACCESS_TOKEN,
            "sub": user_id,
            "email": email,
            "roles": roles,
            "jti": str(uuid.uuid4()),
        }

        return jwt.encode(
            payload=payload,
            key=self.private_key,
            algorithm="RS256",
        )

    def decode_access_token(self, token: str) -> dict:
        """Decode jwt token.

        Raises
        ------
            ExpiredJWTError: token expired
            InvalidTokenError: incorrect token
            InvalidScopeError: invalid scope
        """
        try:
            payload: dict = jwt.decode(token, self.public_key, algorithms=["RS256"])
        except jwt.ExpiredSignatureError:
            raise ExpiredJwtError
        except jwt.InvalidTokenError:
            raise InvalidTokenError
        if payload["scope"] == Scope.ACCESS_TOKEN:
            return payload
        raise InvalidScopeError(payload["scope"])

    def decode_token(self, token: str) -> dict:
        """Decode any jwt token.

        Raises
        ------
            ExpiredJwtError: token expired
            InvalidTokenError: incorrect token
        """
        try:
            payload: dict = jwt.decode(token, self.public_key, algorithms=["RS256"])
        except jwt.ExpiredSignatureError:
            raise ExpiredJwtError
        except jwt.InvalidTokenError:
            raise InvalidTokenError
        return payload

    def encode_refresh_token(self, user_id: str, email: str, roles: list[str]) -> str:
        payload = {
            "exp": datetime.utcnow() + self.access_token_lifetime,
            "iat": datetime.utcnow(),
            "scope": Scope.REFRESH_TOKEN,
            "sub": user_id,
            "email": email,
            "roles": roles,
            "jti": str(uuid.uuid4()),
        }

        return jwt.encode(
            payload=payload,
            key=self.private_key,
            algorithm="RS256",
        )

    def refresh_token(self, refresh_token: str) -> str:
        """Generate new token by refresh token.

        Raises
        ------
            ExpiredJwtError: token expired
            InvalidTokenError: incorrect token
            InvalidScopeError: invalid scope
        """
        try:
            payload: dict = jwt.decode(refresh_token, self.public_key, algorithms=["RS256"])
        except jwt.ExpiredSignatureError:
            raise ExpiredJwtError
        except jwt.InvalidTokenError:
            raise InvalidTokenError
        if payload["scope"] == Scope.REFRESH_TOKEN:
            user_id = payload["sub"]
            return self.encode_access_token(user_id, payload["email"], payload["roles"])
        raise InvalidScopeError(payload["scope"])

    def get_timedelta(self, token: str) -> timedelta:
        """Get timedelta until token expire.

        Raises
        ------
            ExpiredJwtError: token expired
            InvalidTokenError: incorrect token
        """
        try:
            payload: dict = jwt.decode(token, self.public_key, algorithms=["RS256"])
        except jwt.ExpiredSignatureError:
            raise ExpiredJwtError
        except jwt.InvalidTokenError:
            raise InvalidTokenError

        expire_datetime = datetime.fromtimestamp(payload["exp"])
        return expire_datetime - datetime.utcnow()


@lru_cache
def get_jwt_service() -> JWTService:
    with open(s.rsa_private_path, "r") as priv_obj:
        with open(s.rsa_public_path, "r") as pub_obj:
            return JWTService(
                private_key=priv_obj.read(),
                public_key=pub_obj.read(),
                access_token_lifetime=s.access_token_lifetime,
                refresh_token_lifetime=s.refresh_token_lifetime,
            )
