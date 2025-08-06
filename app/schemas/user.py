from fastapi_users import schemas
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(alias='email')
    password: str

    class Config:
        populate_by_name = True


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


class ExcludeFields(BaseModel):
    is_active: bool = Field(exclude=True, default=True)
    is_superuser: bool = Field(exclude=True, default=False)
    is_verified: bool = Field(exclude=True, default=False)


class UserRead(ExcludeFields, schemas.BaseUser[int]):
    class Config:
        populate_by_name = True


class UserCreate(schemas.BaseUserCreate): ...
