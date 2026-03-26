from fastapi_users import schemas
from pydantic import BaseModel, Field


class LoginRequestSchema(BaseModel):
    username: str = Field(alias='email')
    password: str

    class Config:
        populate_by_name = True


class LoginResponseSchema(BaseModel):
    access_token: str
    token_type: str


class UserReadSchema(schemas.BaseUser[int]): ...


class UserCreateSchema(schemas.BaseUserCreate): ...
