from fastapi_users import BaseUserManager, IntegerIDMixin

from app.models.user import User


class UserManager(IntegerIDMixin, BaseUserManager[User, int]): ...
