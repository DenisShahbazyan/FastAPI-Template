import os
from typing import Any

from pydantic import BaseModel, PostgresDsn, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DB(BaseModel):
    host: str = 'localhost'
    port: int = 5432
    username: str = 'postgres'
    password: str = 'postgres'
    name: str = 'test_db'
    url: str = 'postgresql+asyncpg://postgres:postgres@localhost:5432/test_db'

    @model_validator(mode='after')
    def assemble_dsn(cls, values: dict[str, Any]) -> dict[str, Any]:  # noqa N805
        values.url = PostgresDsn.build(
            scheme='postgresql+asyncpg',
            username=values.username,
            password=values.password,
            host=values.host,
            port=values.port,
            path=values.name,
        )
        values.url = str(values.url)
        return values


class JWT(BaseModel):
    SECRET: str = '7X9QWN3P2R5T8V1Y4Z7B6D9F3G6H8J2K4M7N9P2Q5S7U1W3Y5A1C4E6F8H2J4L'
    ACCESS_TOKEN_LIFETIME_SECONDS: int = 60 * 60  # 1 hour
    REFRESH_TOKEN_LIFETIME_SECONDS: int = 60 * 60 * 24 * 7  # 7 days


def get_env_file(environment: str | None) -> str:
    match environment:
        case 'docker':
            return '.env.docker'
        case _:
            return '.env.local'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            '.env.template',
            get_env_file(os.getenv('ENVIRONMENT')),
        ),
        case_sensitive=False,
        env_nested_delimiter='__',
    )

    db: DB = DB()
    jwt: JWT = JWT()


settings = Settings()
