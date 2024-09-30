from typing import AsyncGenerator

from fastapi import Depends

from app.core.auth.dependencies.db import get_user_db
from app.core.auth.manager import UserManager


async def get_user_manager(
    user_db=Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)
