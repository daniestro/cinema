import abc
import uuid

from auth_app.services.misc import JWTPair


class OAuthServiceInterface(abc.ABC):
    @abc.abstractmethod
    async def authorize(
        self,
        oauth_info: dict,
        user_agent: str | None,
        ip: str | None,
    ) -> JWTPair:
        """Authorize using OAuth.

        If user doesn't exist, create it with random strong password
        """

    @abc.abstractmethod
    async def bind(
        self,
        user_id: uuid.UUID,
        oauth_info: dict,
    ) -> JWTPair:
        """Bind oauth-account to already exists account."""
