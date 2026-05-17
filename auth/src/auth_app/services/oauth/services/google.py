import uuid

from auth_app.errors.external import SocialnetNotFound, UserNotFound
from auth_app.services.misc import JWTPair, generate_jwt

from .base import OAuthBaseService
from .misc import generate_password


class OAuthGoogleService(OAuthBaseService):
    async def authorize(
        self,
        oauth_info: dict,
        user_agent: str | None,
        ip: str | None,
    ) -> JWTPair:
        email = oauth_info["email"]
        oauth_id = oauth_info["id"]
        try:
            socialnet = await self.socalnet_repository.get_by_oauth_id(oauth_id)
            user = await self.user_service.get(socialnet.user_id)
        except (UserNotFound, SocialnetNotFound):
            user = await self.user_service.create(email, password=generate_password(20))
            socialnet = await self.socalnet_repository.create(user_id=user.id, oauth_id=oauth_id, email=email)

        role_names = [role.name for role in user.roles]
        jwt = generate_jwt(self.jwt_service, str(user.id), user.email, role_names)

        await self.login_history_repository.create_record(
            user_id=user.id,
            user_agent=str(user_agent),
            ip=str(ip),
            access_jti=jwt.jti.access,
            refresh_jti=jwt.jti.refresh,
        )

        self.logger.info("Successfully google oauth email=%s", email)
        return jwt.tokens

    async def bind(self, user_id: uuid.UUID, oauth_info: dict):
        email = oauth_info["email"]
        oauth_id = oauth_info["id"]
        await self.socalnet_repository.create(user_id=user_id, oauth_id=oauth_id, email=email)

        self.logger.info("Bind google %s: %s", email, user_id)
