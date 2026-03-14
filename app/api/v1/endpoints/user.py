from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users.authentication.strategy.jwt import JWTStrategy
from fastapi_users.manager import BaseUserManager
from fastapi_users.router.common import ErrorCode

from app.api.v1.utils.user import (
    hide_standard_route,
    set_refresh_token_cookie,
)
from app.core.auth.backend import (
    auth_backend,
    get_access_jwt_strategy,
    get_refresh_jwt_strategy,
)
from app.core.auth.users import current_user, fastapi_users
from app.core.config import settings
from app.models.user import User
from app.schemas.v1.user import (
    LoginRequestSchema,
    LoginResponseSchema,
    UserCreateSchema,
    UserReadSchema,
)

router = APIRouter()

# ═══════════════════════════════════════════════════════════
# Стандартные роутеры fastapi-users
# ═══════════════════════════════════════════════════════════

router.include_router(
    fastapi_users.get_auth_router(
        auth_backend,
        requires_verification=settings.jwt.REQUIRES_VERIFICATION,
    ),
    prefix='/auth',
    tags=['auth'],
)

router.include_router(
    fastapi_users.get_register_router(UserReadSchema, UserCreateSchema),
    prefix='/auth',
    tags=['auth'],
)

# ═══════════════════════════════════════════════════════════
# Переопределение стандартных путей fastapi-users
# ═══════════════════════════════════════════════════════════

hide_standard_route(router, current_path='/auth/login', new_path='/login')
hide_standard_route(router, current_path='/auth/logout')

# ═══════════════════════════════════════════════════════════
# Кастомные роутеры
# ═══════════════════════════════════════════════════════════


@router.post('/auth/login', tags=['auth'])
async def login(
    request: Request,
    credentials: LoginRequestSchema,
    user_manager: BaseUserManager[User, int] = Depends(fastapi_users.get_user_manager),
    access_strategy: JWTStrategy[User, int] = Depends(get_access_jwt_strategy),
    refresh_strategy: JWTStrategy[User, int] = Depends(get_refresh_jwt_strategy),
) -> Response:
    user = await user_manager.authenticate(
        OAuth2PasswordRequestForm(
            username=credentials.username,
            password=credentials.password,
        )
    )
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
        )
    if settings.jwt.REQUIRES_VERIFICATION and not user.is_verified:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=ErrorCode.LOGIN_USER_NOT_VERIFIED,
        )

    response = await auth_backend.login(access_strategy, user)
    response = await set_refresh_token_cookie(user, response, refresh_strategy)
    await user_manager.on_after_login(user, request, response)
    return response


@router.post('/auth/logout', tags=['auth'])
async def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(key='refresh_token')
    return {'message': 'Успешный выход'}


@router.post('/auth/refresh', tags=['auth'])
async def refresh_token(
    request: Request,
    user_manager: BaseUserManager[User, int] = Depends(fastapi_users.get_user_manager),
    access_strategy: JWTStrategy[User, int] = Depends(get_access_jwt_strategy),
    refresh_strategy: JWTStrategy[User, int] = Depends(get_refresh_jwt_strategy),
) -> LoginResponseSchema:
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail='Отсутствует refresh токен'
        )

    user = await refresh_strategy.read_token(refresh_token, user_manager)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail='Недействительный refresh токен'
        )
    if not user.is_active:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail='Недействительный пользователь'
        )

    access_token = await access_strategy.write_token(user)
    return LoginResponseSchema(access_token=access_token, token_type='bearer')


@router.get('/me', tags=['users'])
async def me(current_user: UserReadSchema = Depends(current_user)) -> UserReadSchema:
    return current_user


@router.get('/auth/token', tags=['auth'])
async def validate_token(current_user: User = Depends(current_user)) -> bool:
    return True
