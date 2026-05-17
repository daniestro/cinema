import abc


class OAuthProviderInterface(abc.ABC):
    @abc.abstractmethod
    def get_oauth_url(self, redirect_url: str | None = None) -> str:
        """Generate OAuth link."""

    @abc.abstractmethod
    async def exchange_token(self, code: str, redirect_url: str | None = None) -> str:
        """Exchange OAuth code for access token."""

    @abc.abstractmethod
    async def get_user_info(self, access_token: str) -> dict:
        """Get user info in dict."""
