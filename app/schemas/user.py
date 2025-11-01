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


class ExcludeFields(BaseModel):
    is_active: bool = Field(exclude=True, default=True)
    is_superuser: bool = Field(exclude=True, default=False)
    is_verified: bool = Field(exclude=True, default=False)


class UserReadSchema(ExcludeFields, schemas.BaseUser[int]):
    class Config:
        populate_by_name = True


class UserCreateSchema(schemas.BaseUserCreate): ...
