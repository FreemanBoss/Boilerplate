from typing import TYPE_CHECKING, Optional
from sqlalchemy.orm import (
    mapped_column,
    Mapped,
    relationship
)
from sqlalchemy import ForeignKey

from api.database.database import Base, ModelMixin
from api.v1.user_device.model import UserDevice

if TYPE_CHECKING:
    from api.v1.user.model import User
    


class ActivityLog(ModelMixin, Base):
    """
    Represents activity_logs table in the database.
    """
    __tablename__ = "activity_logs"
    user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    target_user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    device_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("user_devices.id", ondelete="SET NULL"), nullable=True
    )
    action_type: Mapped[str]
    action_details: Mapped[Optional[str]] = mapped_column(nullable=True)
    ip_address: Mapped[str]
    location: Mapped[Optional[str]] = mapped_column(nullable=True)
    
    user: Mapped["User"] = relationship(
        "User", uselist=False, back_populates="activities", foreign_keys=[user_id]
    )
    target_user: Mapped["User"] = relationship(
        "User", uselist=False, back_populates="target_activities", foreign_keys=[target_user_id]
    )
    device: Mapped["UserDevice"] = relationship(
        "UserDevice", uselist=False, back_populates="activities", foreign_keys=[device_id]
    )
