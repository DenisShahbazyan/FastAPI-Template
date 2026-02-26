import os
from pathlib import Path
from typing import Self

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, PostgresDsn, ValidationInfo, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
APP_DIR: Path = PROJECT_DIR / 'app'
STATIC_DIR: Path = PROJECT_DIR / 'static'


class DB(BaseModel):
    host: str = 'localhost'
    port: int = 5432
    username: str = 'postgres'
    password: str = 'postgres'
    name: str = 'fastapi_db'
    url: str = 'postgresql+asyncpg://postgres:postgres@localhost:5432/fastapi_db'

    POOL_SIZE: int = 20
    MAX_OVERFLOW: int = 10
    POOL_TIMEOUT: int = 30
    POOL_RECYCLE: int = 1800
    ECHO: bool = False

    @model_validator(mode='after')
    def assemble_dsn(self, validation_info: ValidationInfo) -> Self:
        self.url = str(
            PostgresDsn.build(
                scheme='postgresql+asyncpg',
                username=self.username,
                password=self.password,
                host=self.host,
                port=int(self.port),
                path=self.name,
            )
        )
        return self


class JWT(BaseModel):
    SECRET: str = '7X9QWN3P2R5T8V1Y4Z7B6D9F3G6H8J2K4M7N9P2Q5S7U1W3Y5A1C4E6F8H2J4L'
    ACCESS_TOKEN_LIFETIME_SECONDS: int = 60 * 60  # 1 hour
    REFRESH_TOKEN_LIFETIME_SECONDS: int = 60 * 60 * 24 * 7  # 7 days


class Static(BaseModel):
    DIR: Path = STATIC_DIR
    URL: str = '/static'
    DOCS_JS: str = '/static/docs/swagger-ui-bundle.js'
    DOCS_CSS: str = '/static/docs/swagger-ui.css'
    REDOC_JS: str = '/static/docs/redoc.standalone.js'


def get_env_file(environment: str | None) -> Path:
    match environment:
        case 'docker':
            return PROJECT_DIR / '.env.docker'
        case _:
            return PROJECT_DIR / '.env.local'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_env_file(os.getenv('ENVIRONMENT')),
        case_sensitive=False,
        env_nested_delimiter='__',
    )

    db: DB = DB()
    jwt: JWT = JWT()
    static: Static = Static()


settings = Settings()


def mount_static(app: FastAPI) -> None:
    settings.static.DIR.mkdir(parents=True, exist_ok=True)
    app.mount(
        settings.static.URL,
        StaticFiles(directory=settings.static.DIR),
        name='static',
    )
