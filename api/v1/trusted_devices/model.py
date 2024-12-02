from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum

from typing import TYPE_CHECKING
from sqlalchemy import Boolean, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship


from api.database.database import Base, ModelMixin


if  TYPE_CHECKING:
    from api.v1.comment.model import PhotoComment
    from api.v1.like.model import PhotoLike  

class TrustedDevice(ModelMixin, Base):
    """Model for storing trusted devices."""

    __tablename__ = "trusted_devices"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    device_id: Mapped[str] = mapped_column(String, nullable=False)
    platform: Mapped[str] = mapped_column(String, nullable=False)
    device_name: Mapped[str] = mapped_column(String, nullable=False)
    last_used_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    is_trusted: Mapped[bool] = mapped_column(Boolean, default=True)

    user = relationship("User", back_populates="trusted_devices")
