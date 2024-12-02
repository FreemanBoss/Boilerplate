from typing import TYPE_CHECKING, Optional
from sqlalchemy.orm import (
    Mapped,
    relationship,
    mapped_column
)
from sqlalchemy import ForeignKey, String

from api.database.database import Base, ModelMixin

if TYPE_CHECKING:
    from api.v1.user.model import User
    from api.v1.activity_log.model import ActivityLog



class UserDevice(ModelMixin, Base):
    """
    Represents user_devices table in the database.
    """
    __tablename__ = "user_devices"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    device_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    device_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    # Relationships
    user: Mapped["User"] = relationship("User", uselist=False, back_populates="user_devices")
    activities: Mapped["ActivityLog"] = relationship("ActivityLog", back_populates="device", passive_deletes=True)

    def __str__(self):
        return f"UserDevice(id={self.id}, user_id={self.user_id}, device_type={self.device_type}, device_token={self.device_token})"
