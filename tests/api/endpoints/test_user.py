from http import HTTPStatus
from uuid import uuid4

from httpx import AsyncClient

from tests.utils.user import (
    auth_user_request,
    refresh_token_request,
    register_user_request,
)


async def test_register_user_success(async_client: AsyncClient) -> None:
    """
    Проверка что POST запрос на регистрацию пользователя возвращает статус 201
    Проверка что в теле возвращается id
    Проверка что в теле возвращается email
    Проверка что пользователь зарегистрирован с правильным email
    Проверка что в теле не возвращается password

    Args:
        async_client (AsyncClient): Тестовый асинхронный клиент
    """
    email = f'test_{uuid4()}@example.com'

    registered_user = await register_user_request(async_client, email)

    assert registered_user.status_code == HTTPStatus.CREATED

    response_data = registered_user.json()
    assert 'id' in response_data
    assert 'email' in response_data
    assert response_data['email'] == email
    assert 'password' not in response_data


async def test_register_failed_double_email(async_client: AsyncClient) -> None:
    """
    Проверка что POST запрос на регистрацию пользователя с уже существующим email
    возвращает статус 400
    Проверка что в теле возвращается 'REGISTER_USER_ALREADY_EXISTS'

    Args:
        async_client (AsyncClient): Тестовый асинхронный клиент
    """
    email = f'test_{uuid4()}@example.com'

    await register_user_request(async_client, email)
    registered_user = await register_user_request(async_client, email)

    assert registered_user.status_code == HTTPStatus.BAD_REQUEST
    assert registered_user.json()['detail'] == 'REGISTER_USER_ALREADY_EXISTS'


async def test_register_invalid_email(async_client: AsyncClient) -> None:
    """
    Проверка регистрации с невалидным email

    Args:
        async_client (AsyncClient): Тестовый асинхронный клиент
    """
    response = await register_user_request(async_client, 'invalid-email')
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_register_missing_password(async_client: AsyncClient) -> None:
    """
    Проверка регистрации без пароля

    Args:
        async_client (AsyncClient): Тестовый асинхронный клиент
    """
    response = await async_client.post(
        url='/v1/auth/register',
        json={'email': 'test@example.com'},
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_login_success(async_client: AsyncClient) -> None:
    """
    Проверка что POST запрос на логин существующего пользователя возвращает статус 200

    Args:
        async_client (AsyncClient): Тестовый асинхронный клиент
    """
    email = f'test_{uuid4()}@example.com'

    await register_user_request(async_client, email)

    response = await auth_user_request(async_client, email)

    assert response.status_code == HTTPStatus.OK, response.text


async def test_login_invalid_credentials(async_client: AsyncClient) -> None:
    """
    Проверка что POST запрос на логин с неправильными данными возвращает статус 400
    Проверка что в теле возвращается 'LOGIN_BAD_CREDENTIALS'

    Args:
        async_client (AsyncClient): description
    """
    response = await auth_user_request(async_client, 'testuser', 'wrongpassword')

    assert response.status_code == HTTPStatus.BAD_REQUEST, response.text
    assert response.json()['detail'] == 'LOGIN_BAD_CREDENTIALS'


async def test_login_with_email_case_insensitive(async_client: AsyncClient) -> None:
    """
    Проверка логина с разным регистром email

    Args:
        async_client (AsyncClient): Тестовый асинхронный клиент
    """
    email = f'test_{uuid4()}@example.com'

    await register_user_request(async_client, email)

    response = await auth_user_request(async_client, email.upper())

    assert response.status_code == HTTPStatus.OK


async def test_login_with_whitespace(async_client: AsyncClient) -> None:
    """
    Проверка логина с пробелами в данных

    Args:
        async_client (AsyncClient): Тестовый асинхронный клиент
    """
    email = f'test_{uuid4()}@example.com'

    await register_user_request(async_client, email)

    response = await auth_user_request(async_client, f' {email} ')

    assert response.status_code == HTTPStatus.BAD_REQUEST


# TESTS FOR REFRESH
async def test_refresh_token_success(async_client: AsyncClient) -> None:
    """
    Проверка что POST запрос на обновление токена возвращает статус 200
    Проверка что в теле возвращается новый access_token
    Проверка что в теле возвращается token_type

    Args:
        async_client (AsyncClient): Тестовый асинхронный клиент
    """
    email = f'test_{uuid4()}@example.com'

    await register_user_request(async_client, email)

    login_response = await auth_user_request(async_client, email)
    refresh_token = login_response.cookies.get('refresh_token')

    refresh_response = await refresh_token_request(
        async_client=async_client,
        cookies={'refresh_token': refresh_token} if refresh_token else None,
    )

    assert refresh_response.status_code == HTTPStatus.OK

    response_data = refresh_response.json()
    assert 'access_token' in response_data
    assert 'token_type' in response_data
    assert response_data['token_type'] == 'bearer'


async def test_refresh_token_invalid_token(async_client: AsyncClient) -> None:
    """
    Проверка что POST запрос на обновление с невалидным токеном возвращает статус 401
    Проверка что в теле возвращается 'Недействительный refresh токен'

    Args:
        async_client (AsyncClient): Тестовый асинхронный клиент
    """
    response = await refresh_token_request(
        async_client=async_client,
        cookies={'refresh_token': 'invalid_token'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == 'Недействительный refresh токен'


async def test_refresh_token_missing_token(async_client: AsyncClient) -> None:
    """
    Проверка что POST запрос на обновление без токена возвращает статус 401
    Проверка что в теле возвращается 'Отсутствует refresh токен'

    Args:
        async_client (AsyncClient): Тестовый асинхронный клиент
    """
    response = await refresh_token_request(async_client=async_client)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == 'Отсутствует refresh токен'


async def test_logout_success(async_client: AsyncClient) -> None:
    """
    Проверка что POST запрос на логаут возвращает статус 200
    Проверка что refresh_token удаляется из cookies
    Проверка что в теле возвращается 'Успешный выход'

    Args:
        async_client (AsyncClient): Тестовый асинхронный клиент
    """
    email = f'test_{uuid4()}@example.com'

    await register_user_request(async_client, email)

    login_response = await auth_user_request(async_client, email)
    refresh_token = login_response.cookies.get('refresh_token')

    response = await async_client.post(
        url='/v1/auth/logout',
        headers={'Authorization': f'Bearer {login_response.json()["access_token"]}'},
        cookies={'refresh_token': refresh_token} if refresh_token else None,
    )

    assert response.status_code == HTTPStatus.OK
    assert not response.cookies.get('refresh_token')
    assert response.json()['message'] == 'Успешный выход'


async def test_token_endpoint_success(async_client: AsyncClient) -> None:
    """
    Проверка что GET запрос для авторизованного пользователя на эндпоинт возвращает
    статус 200
    Проверка что в теле возвращается true
    Проверка что GET запрос для НЕ авторизованного пользователя на эндпоинт возвращает
    статус 401

    Args:
        async_client (AsyncClient): Тестовый асинхронный клиент
    """
    email = f'test_{uuid4()}@example.com'

    await register_user_request(async_client, email)

    login_response = await auth_user_request(async_client, email)

    response = await async_client.get(
        url='/v1/auth/token',
        headers={'Authorization': f'Bearer {login_response.json()["access_token"]}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()

    response = await async_client.get(url='/v1/auth/token')

    assert response.status_code == HTTPStatus.UNAUTHORIZED


async def test_me_endpoint_success(async_client: AsyncClient) -> None:
    """
    Проверка что GET запрос для авторизованного пользователя на эндпоинт возвращает
    статус 200
    Проверка что в теле возвращается email

    Args:
        async_client (AsyncClient): Тестовый асинхронный клиент
    """
    email = f'test_{uuid4()}@example.com'

    await register_user_request(async_client, email)

    login_response = await auth_user_request(async_client, email)

    response = await async_client.get(
        url='/v1/me',
        headers={'Authorization': f'Bearer {login_response.json()["access_token"]}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['email'] == email


async def test_me_endpoint_no_auth(async_client: AsyncClient) -> None:
    """
    Проверка что GET запрос для НЕ авторизованного пользователя на эндпоинт возвращает
    статус 401

    Args:
        async_client (AsyncClient): Тестовый асинхронный клиент
    """
    response = await async_client.get(url='/v1/me')

    assert response.status_code == HTTPStatus.UNAUTHORIZED
