from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi_users.authentication import AuthenticationBackend, Authenticator
from fastapi_users.authentication.strategy.jwt import JWTStrategy
from fastapi_users.manager import BaseUserManager
from fastapi_users.router.common import ErrorCode

from app.api.utils.user import modify_standart_auth_endpoints, set_refresh_token_cookie
from app.core.auth.backend import (
    auth_backend,
    get_access_jwt_strategy,
    get_refresh_jwt_strategy,
)
from app.core.auth.users import current_user, fastapi_users
from app.models.user import User
from app.schemas.user import LoginRequest, LoginResponse, UserCreate, UserRead

router = APIRouter()


@router.post('/auth/logout', tags=['auth'])
async def logout(request: Request, response: Response):
    response.delete_cookie(key='refresh_token')
    return {'message': 'Успешный выход'}


router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/auth',
    tags=['auth'],
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix='/auth',
    tags=['auth'],
)


modify_standart_auth_endpoints(router, '/auth/login', '/login')
# modify_standard_logout_endpoints(router)


def get_auth_router(
    backend: AuthenticationBackend,
    get_user_manager: BaseUserManager,
    authenticator: Authenticator,
    requires_verification: bool = False,
):
    router = APIRouter()

    @router.post('/login')
    async def login(
        request: Request,
        credentials: LoginRequest,
        user_manager: BaseUserManager = Depends(get_user_manager),
        access_strategy: JWTStrategy = Depends(get_access_jwt_strategy),
        refresh_strategy: JWTStrategy = Depends(get_refresh_jwt_strategy),
    ) -> LoginResponse:
        user = await user_manager.authenticate(credentials)
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
            )
        if requires_verification and not user.is_verified:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=ErrorCode.LOGIN_USER_NOT_VERIFIED,
            )
        response = await backend.login(access_strategy, user)
        response = await set_refresh_token_cookie(user, response, refresh_strategy)
        await user_manager.on_after_login(user, request, response)
        return response

    return router


router.include_router(
    get_auth_router(
        backend=auth_backend,
        get_user_manager=fastapi_users.get_user_manager,
        authenticator=fastapi_users.authenticator,
        requires_verification=False,
    ),
    prefix='/auth',
    tags=['auth'],
)


@router.post('/auth/refresh', tags=['auth'])
async def refresh_token(
    request: Request,
    user_manager: BaseUserManager[User, int] = Depends(fastapi_users.get_user_manager),
    access_strategy: JWTStrategy = Depends(get_access_jwt_strategy),
    refresh_strategy: JWTStrategy = Depends(get_refresh_jwt_strategy),
) -> LoginResponse:
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
    return LoginResponse(access_token=access_token, token_type='bearer')


@router.get('/me', tags=['users'])
async def me(current_user: User = Depends(current_user)) -> UserRead:
    return current_user


@router.get('/auth/token', tags=['auth'])
async def validate_token(current_user: User = Depends(current_user)) -> bool:
    return True
