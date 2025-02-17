from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users.db import BaseUserDatabase

from app.core.auth.dependencies.db import get_user_db
from app.core.auth.manager import UserManager
from app.models.user import User


async def get_user_manager(
    user_db: BaseUserDatabase[User, int] = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)
