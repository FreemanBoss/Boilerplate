from typing import Optional, TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database.database import Base, ModelMixin
from api.v1.enum_types import notification_status_enum, notification_type_enum

if TYPE_CHECKING:
    from api.v1.user.model import User


class Notification(ModelMixin, Base):
    """
    represents the notification table in the database.
    """

    message: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    notification_type: Mapped[str] = mapped_column(
        notification_type_enum,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(notification_status_enum, default="pending")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    title: Mapped[str]

    user: Mapped["User"] = relationship(
        "User", uselist=False, back_populates="notifications"
    )

    def mark_as_read(self):
        """Marks the notification as read."""
        self.is_read = True
        self.status = "sent"

    def __str__(self):
        return f"Notification to User {self.user_id}: {self.message} (Type: {self.notification_type})"


class PushNotification(ModelMixin, Base):
    """
    represents the push_notification table in the database.
    """

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        comment="References the user to whom the push notification is sent",
    )
    device_token_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("user_devices.id", ondelete="SET NULL"),
        nullable=False,
        comment="References the device token for this push",
    )
    notification_id: Mapped[str] = mapped_column(
        ForeignKey("notifications.id", ondelete="SET NULL"),
        nullable=False,
        comment="References the notification associated with this push",
    )
    status: Mapped[str] = mapped_column(
        notification_status_enum,
        default="pending",
        nullable=False,
        comment="Status of the push ('pending', 'sent', 'failed')",
    )
    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of attempts to resend if it fails",
    )
    last_attempt_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp of the last attempt to send the push",
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User", uselist=False, back_populates="push_notifications"
    )

    def increment_retry_count(self):
        """Increments the retry count and updates the last attempt timestamp."""
        self.retry_count += 1
        self.last_attempt_at = func.now()

    def __str__(self):
        return (
            f"PushNotification(id={self.id}, user_id={self.user_id}, status={self.status}, "
            f"retry_count={self.retry_count}, last_attempt_at={self.last_attempt_at})"
        )
