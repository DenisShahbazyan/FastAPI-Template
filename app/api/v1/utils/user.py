from fastapi import APIRouter, Response
from fastapi.routing import APIRoute
from fastapi_users.authentication.strategy.jwt import JWTStrategy
from starlette.routing import compile_path

from app.core.config import settings
from app.models.user import User


def hide_standard_route(
    router: APIRouter,
    *,
    current_path: str,
    new_path: str | None = None,
) -> None:
    """Скрыть стандартный роут fastapi-users из схемы.

    Если передан `new_path` — роут переносится на новый путь (например,
        стандартный form-login → `/login` для OAuth2PasswordBearer в Swagger).
    Без `new_path` — роут удаляется из роутера, освобождая путь для кастомной реализации
    """
    if new_path is not None:
        for route in router.routes:
            if isinstance(route, APIRoute) and route.path == current_path:
                route.path = new_path
                route.path_regex, route.path_format, route.param_convertors = (
                    compile_path(new_path)
                )
                route.include_in_schema = False
    else:
        router.routes = [
            route
            for route in router.routes
            if not (isinstance(route, APIRoute) and route.path == current_path)
        ]


async def set_refresh_token_cookie(
    user: User,
    response: Response,
    refresh_strategy: JWTStrategy[User, int],
) -> Response:
    refresh_token = await refresh_strategy.write_token(user)
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite='none',
        max_age=settings.jwt.REFRESH_TOKEN_LIFETIME_SECONDS,
    )
    return response
