from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.responses import HTMLResponse

SWAGGER_JS_URL = (
    'https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/swagger-ui-bundle.js'
)
SWAGGER_CSS_URL = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/swagger-ui.css'
REDOC_JS_URL = 'https://cdn.jsdelivr.net/npm/redoc@latest/bundles/redoc.standalone.js'


def _get_openapi_url(app: FastAPI) -> str:
    if app.openapi_url is None:
        raise ValueError('openapi_url is None')
    return app.openapi_url


def _setup_swagger(
    app: FastAPI,
    docs_url: str,
    swagger_js_url: str,
    swagger_css_url: str,
) -> None:
    @app.get(docs_url, include_in_schema=False)
    async def swagger_ui_html() -> HTMLResponse:
        return get_swagger_ui_html(
            openapi_url=_get_openapi_url(app),
            title=f'{app.title} - Swagger UI',
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url=swagger_js_url,
            swagger_css_url=swagger_css_url,
        )

    @app.get(
        app.swagger_ui_oauth2_redirect_url or '/docs/oauth2-redirect',
        include_in_schema=False,
    )
    async def swagger_ui_redirect() -> HTMLResponse:
        return get_swagger_ui_oauth2_redirect_html()


def _setup_redoc(
    app: FastAPI,
    redoc_url: str,
    redoc_js_url: str,
) -> None:
    @app.get(redoc_url, include_in_schema=False)
    async def redoc_html() -> HTMLResponse:
        return get_redoc_html(
            openapi_url=_get_openapi_url(app),
            title=f'{app.title} - ReDoc',
            redoc_js_url=redoc_js_url,
        )


def get_custom_docs(
    app: FastAPI,
    docs_url: str | None = '/docs',
    swagger_js_url: str = SWAGGER_JS_URL,
    swagger_css_url: str = SWAGGER_CSS_URL,
    redoc_url: str | None = '/redoc',
    redoc_js_url: str = REDOC_JS_URL,
) -> None:
    """Настройка кастомных путей к статике для Swagger и ReDoc.

    Перед использованием отключите стандартную документацию:
    `app = FastAPI(docs_url=None, redoc_url=None)`

    Args:
        app: Экземпляр приложения FastAPI.
        docs_url: URL для Swagger UI. None — отключить.
        swagger_js_url: URL для swagger-ui-bundle.js.
        swagger_css_url: URL для swagger-ui.css.
        redoc_url: URL для ReDoc. None — отключить.
        redoc_js_url: URL для redoc.standalone.js.

    Пример использования:
    ```python
    get_custom_docs(
        app,
        docs_url='/docs',
        swagger_js_url=settings.static.DOCS_JS,
        swagger_css_url=settings.static.DOCS_CSS,
        redoc_url='/redoc',
        redoc_js_url=settings.static.REDOC_JS,
    )
    ```
    """
    if docs_url is not None:
        _setup_swagger(app, docs_url, swagger_js_url, swagger_css_url)

    if redoc_url is not None:
        _setup_redoc(app, redoc_url, redoc_js_url)
