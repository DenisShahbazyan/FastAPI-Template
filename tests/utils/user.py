from unittest.mock import patch

from httpx import AsyncClient, Response


async def register_user_request(
    async_client: AsyncClient,
    email: str,
    password: str = 'string',
) -> Response:
    """
    Регистрация пользователя, с замоканным в None on_after_register

    Args:
        async_client (AsyncClient): Тестовый асинхронный клиент
        email (str): Email для регистрации пользователя
        password (str, optional): Пароль для регистрации пользователя.
            По умолчанию 'string'.

    Returns:
        Response: Ответ от сервера
    """
    with patch(
        'app.core.auth.manager.UserManager.on_after_register',
        return_value=None,
    ):
        response = await async_client.post(
            url='/v1/auth/register',
            json={
                'email': email,
                'password': password,
            },
        )
        return response


async def auth_user_request(
    async_client: AsyncClient,
    email: str,
    password: str = 'string',
) -> Response:
    """
    Авторизация пользователя, с замоканным в None on_after_login

    Args:
        async_client (AsyncClient): Тестовый асинхронный клиент
        email (str): Email для логина пользователя
        password (str, optional): Пароль для логина пользователя.
            По умолчанию 'string'.

    Returns:
        Response: Ответ от сервера
    """
    with patch(
        'app.core.auth.manager.UserManager.on_after_login',
        return_value='Mocked implementation',
    ):
        response = await async_client.post(
            url='/v1/auth/login',
            json={
                'email': email,
                'password': password,
            },
        )
        return response


async def refresh_token_request(
    async_client: AsyncClient,
    cookies: dict[str, str] | None = None,
) -> Response:
    """
    Обновление токена

    Args:
        async_client (AsyncClient): Тестовый асинхронный клиент
        cookies (dict[str, str]): Куки

    Returns:
        Response: Ответ от сервера
    """
    response = await async_client.post(
        url='/v1/auth/refresh',
        cookies=cookies,
    )
    return response
