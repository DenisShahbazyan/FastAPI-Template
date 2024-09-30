from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

from app.core.config import settings

bearer_transport = BearerTransport(tokenUrl='/login')


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.auth.JWT_SECRET,
        lifetime_seconds=settings.auth.JWT_TOKEN_LIFETIME_SECONDS,
    )


auth_backend = AuthenticationBackend(
    name='jwt',
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
