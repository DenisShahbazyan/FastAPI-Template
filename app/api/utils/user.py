from fastapi import APIRouter, Response
from fastapi.routing import APIRoute
from fastapi_users.authentication.strategy.jwt import JWTStrategy

from app.core.config import settings
from app.models.user import User


def modify_standard_auth_endpoints(
    router: APIRouter, old_path: str, new_path: str
) -> None:
    """### Модификация пути стандартного роутера авторизации в fastapi-users.

    Новый путь в парметрах:

        route.path = '/login'
        route.path_format = '/login'

    должен совпадать с путем в настройках fastapi-users:

        bearer_transport = BearerTransport(tokenUrl='/login')

    если это условие соблюдено - кнопка "Autorize" в swagger будет работать как
    OAuth2PasswordBearer (OAuth2, password)

    Args:
        router (APIRouter): _description_
    """
    for route in router.routes:
        if isinstance(route, APIRoute):
            if route.path == old_path:
                route.path = new_path
                route.path_format = new_path
                route.include_in_schema = False


def modify_standard_logout_endpoints(router: APIRouter) -> None:
    for route in router.routes:
        if isinstance(route, APIRoute):
            if route.path == '/auth/logout':
                route.include_in_schema = False


async def set_refresh_token_cookie(
    user: User, response: Response, refresh_strategy: JWTStrategy[User, int]
) -> Response:
    refresh_token = await refresh_strategy.write_token(user)
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite='lax',
        max_age=settings.jwt.REFRESH_TOKEN_LIFETIME_SECONDS,
    )
    return response
