from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.mixin._utils import get_current_dt_utc


class UpdatedAtMixin:
    updated_at: Mapped[datetime] = mapped_column(
        default=get_current_dt_utc,
        onupdate=get_current_dt_utc,
        server_default=func.now(),
        server_onupdate=func.now(),
    )
