from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi_users.authentication import AuthenticationBackend, Authenticator
from fastapi_users.authentication.strategy.jwt import JWTStrategy
from fastapi_users.manager import BaseUserManager
from fastapi_users.router.common import ErrorCode

from app.api.utils.user import modify_standart_auth_endpoints
from app.core.auth.backend import auth_backend
from app.core.auth.users import fastapi_users
from app.schemas.user import LoginRequest, LoginResponse, UserCreate, UserRead

router = APIRouter()


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
        strategy: JWTStrategy = Depends(backend.get_strategy),
    ) -> LoginResponse:
        user = await user_manager.authenticate(credentials)
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=400,
                detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
            )
        if requires_verification and not user.is_verified:
            raise HTTPException(
                status_code=400,
                detail=ErrorCode.LOGIN_USER_NOT_VERIFIED,
            )
        response = await backend.login(strategy, user)
        await user_manager.on_after_login(user, request, response)
        return response

    return router


router.include_router(
    get_auth_router(
        auth_backend,
        fastapi_users.get_user_manager,
        fastapi_users.authenticator,
        requires_verification=False,
    ),
    prefix='/auth',
    tags=['auth'],
)
