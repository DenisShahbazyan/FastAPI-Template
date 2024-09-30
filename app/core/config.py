from pathlib import Path
from typing import Any, ClassVar

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import PostgresDsn, model_validator
from pydantic_settings import BaseSettings


class App(BaseSettings):
    STATIC_DIR: ClassVar[Path] = Path(__file__).parent.parent.parent / 'static'


class Postgres(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_NAME: str
    DATABASE_URL: PostgresDsn

    @model_validator(mode='before')
    def assemble_dsn(cls, values: dict[str, Any]) -> dict[str, Any]:  # noqa N805
        values['DATABASE_URL'] = PostgresDsn.build(
            scheme='postgresql+asyncpg',
            username=values['DB_USERNAME'],
            password=values['DB_PASSWORD'],
            host=values['DB_HOST'],
            port=int(values['DB_PORT']),
            path=values['DB_NAME'],
        )
        return values


class Auth(BaseSettings):
    JWT_SECRET: str
    JWT_ACCESS_TOKEN_LIFETIME_SECONDS: int
    JWT_REFRESH_TOKEN_LIFETIME_SECONDS: int


class Settings(BaseSettings):
    app: App = App()
    postgres: Postgres = Postgres()
    auth: Auth = Auth()


settings = Settings()


def config_static_folder(app: FastAPI):
    static = settings.app.STATIC_DIR
    static.mkdir(parents=True, exist_ok=True)
    app.mount('/static', StaticFiles(directory=static), name='static')
