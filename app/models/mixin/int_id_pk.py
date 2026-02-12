from sqlalchemy import BigInteger, Identity
from sqlalchemy.orm import Mapped, mapped_column


class IntIdPkMixin:
    """Миксин для добавления поля id (первичного ключа)."""

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
