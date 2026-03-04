from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

from app.core.config import settings
from app.models.user import User

bearer_transport = BearerTransport(tokenUrl='/v1/login')


def get_access_jwt_strategy() -> JWTStrategy[User, int]:
    return JWTStrategy(
        secret=settings.jwt.SECRET,
        lifetime_seconds=settings.jwt.ACCESS_TOKEN_LIFETIME_SECONDS,
        token_audience=['fastapi-users:auth'],
    )


def get_refresh_jwt_strategy() -> JWTStrategy[User, int]:
    return JWTStrategy(
        secret=settings.jwt.SECRET,
        lifetime_seconds=settings.jwt.REFRESH_TOKEN_LIFETIME_SECONDS,
        token_audience=['fastapi-users:refresh'],
    )


auth_backend = AuthenticationBackend(
    name='jwt',
    transport=bearer_transport,
    get_strategy=get_access_jwt_strategy,
)
