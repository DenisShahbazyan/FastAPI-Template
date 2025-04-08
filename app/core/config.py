import os
from pathlib import Path
from typing import Self

from pydantic import BaseModel, PostgresDsn, ValidationInfo, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class DB(BaseModel):
    host: str = 'localhost'
    port: int = 5432
    username: str = 'postgres'
    password: str = 'postgres'
    name: str = 'test_db'
    url: str = 'postgresql+asyncpg://postgres:postgres@localhost:5432/test_db'

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


def get_env_file(environment: str | None) -> str:
    match environment:
        case 'docker':
            return os.path.join(BASE_DIR / '.env.docker')
        case _:
            return os.path.join(BASE_DIR / '.env.local')


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            BASE_DIR / '.env.template',
            BASE_DIR / get_env_file(os.getenv('ENVIRONMENT')),
        ),
        case_sensitive=False,
        env_nested_delimiter='__',
    )

    db: DB = DB()
    jwt: JWT = JWT()


settings = Settings()
