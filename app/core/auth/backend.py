from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

from app.core.config import settings

bearer_transport = BearerTransport(tokenUrl='/login')


def get_access_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.auth.JWT_SECRET,
        lifetime_seconds=settings.auth.JWT_ACCESS_TOKEN_LIFETIME_SECONDS,
        token_audience=['fastapi-users:auth'],
    )


def get_refresh_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.auth.JWT_SECRET,
        lifetime_seconds=settings.auth.JWT_REFRESH_TOKEN_LIFETIME_SECONDS,
        token_audience=['fastapi-users:refresh'],
    )


auth_backend = AuthenticationBackend(
    name='jwt',
    transport=bearer_transport,
    get_strategy=get_access_jwt_strategy,
)
