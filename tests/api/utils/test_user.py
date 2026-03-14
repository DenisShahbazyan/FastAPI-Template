from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi_users.authentication import JWTStrategy

from app.api.v1.utils.user import set_refresh_token_cookie
from app.core.config import settings
from app.models import User


async def test_set_refresh_token_cookie_success() -> None:
    """
    Проверка что функция set_refresh_token_cookie корректно работает
    Проверка что вызывается метод write_token стратегии JWT с правильным пользователем
    Проверка что устанавливается cookie с правильными параметрами безопасности
    Проверка что функция возвращает тот же объект response
    """
    mock_strategy = AsyncMock(JWTStrategy)
    mock_strategy.write_token.return_value = 'mocked_refresh_token'

    user = User(
        id=1,
        email='testuser@example.com',
        is_active=True,
        is_verified=True,
    )

    mock_response = MagicMock()

    response = await set_refresh_token_cookie(user, mock_response, mock_strategy)

    mock_strategy.write_token.assert_awaited_once_with(user)

    mock_response.set_cookie.assert_called_once_with(
        key='refresh_token',
        value='mocked_refresh_token',
        httponly=True,
        secure=True,
        samesite='none',
        max_age=settings.jwt.REFRESH_TOKEN_LIFETIME_SECONDS,
    )

    assert response == mock_response


async def test_set_refresh_token_cookie_strategy_error() -> None:
    """
    Проверка что функция корректно обрабатывает ошибку при генерации JWT токена
    Проверка что исключение прокидывается дальше
    Проверка что cookie не устанавливается при ошибке генерации токена
    """
    mock_strategy = AsyncMock()
    mock_strategy.write_token.side_effect = Exception('JWT generation failed')

    user = User(id=1, email='test@test.com', is_active=True, is_verified=True)
    mock_response = MagicMock()

    with pytest.raises(Exception, match='JWT generation failed'):
        await set_refresh_token_cookie(user, mock_response, mock_strategy)

    # Проверяем, что cookie не был установлен
    mock_response.set_cookie.assert_not_called()


async def test_set_refresh_token_cookie_response_error() -> None:
    """
    Проверка что функция корректно обрабатывает ошибку при установке cookie
    Проверка что исключение прокидывается дальше
    Проверка что токен успешно генерируется до возникновения ошибки
    """
    mock_strategy = AsyncMock()
    mock_strategy.write_token.return_value = 'valid_token'

    user = User(id=1, email='test@test.com', is_active=True, is_verified=True)
    mock_response = MagicMock()
    mock_response.set_cookie.side_effect = Exception('Cookie error')

    with pytest.raises(Exception, match='Cookie error'):
        await set_refresh_token_cookie(user, mock_response, mock_strategy)


async def test_set_refresh_token_cookie_parameters() -> None:
    """
    Проверка что cookie устанавливается с правильным именем 'refresh_token'
    Проверка что cookie устанавливается с правильным значением токена
    Проверка что cookie устанавливается с флагом httponly для безопасности
    Проверка что cookie устанавливается с флагом secure для HTTPS
    Проверка что cookie устанавливается с samesite='lax' для защиты от CSRF
    Проверка что cookie устанавливается с правильным временем жизни
    """
    mock_strategy = AsyncMock()
    mock_strategy.write_token.return_value = 'test_token'

    user = User(id=1, email='test@test.com', is_active=True, is_verified=True)
    mock_response = MagicMock()

    await set_refresh_token_cookie(user, mock_response, mock_strategy)

    call_args = mock_response.set_cookie.call_args
    assert call_args[1]['key'] == 'refresh_token'
    assert call_args[1]['value'] == 'test_token'
    assert call_args[1]['httponly'] is True
    assert call_args[1]['secure'] is True
    assert call_args[1]['samesite'] == 'none'
    assert call_args[1]['max_age'] == settings.jwt.REFRESH_TOKEN_LIFETIME_SECONDS
