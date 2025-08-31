from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable

from app.models.base import Base
from app.models.mixin.created_at import CreatedAtMixin
from app.models.mixin.int_id_pk import IntIdPkMixin
from app.models.mixin.updated_at import UpdatedAtMixin


class User(
    SQLAlchemyBaseUserTable[int],
    Base,
    IntIdPkMixin,
    CreatedAtMixin,
    UpdatedAtMixin,
): ...
