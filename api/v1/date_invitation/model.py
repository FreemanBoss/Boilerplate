from typing import TYPE_CHECKING
from datetime import datetime
from datetime import time
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey

from api.database.database import Base, ModelMixin
from api.v1.enum_types import date_invitation_status_enum

if TYPE_CHECKING:
    from api.v1.user.model import User


class DateInvitation(ModelMixin, Base):
    """
    Represents date_invitations table in the database.
    """

    __tablename__ = "date_invitations"
    inviter_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    invitee_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )

    date_time: Mapped[datetime] = mapped_column()
    destination: Mapped[str] = mapped_column(index=True)
    inviter_pickup_location: Mapped[str] = mapped_column(nullable=True)
    invitee_pickup_location: Mapped[str] = mapped_column(nullable=True)
    inviter_logistic: Mapped[str] = mapped_column(nullable=True)
    invitee_logistic: Mapped[str] = mapped_column(nullable=True)

    inviter_security: Mapped[str] = mapped_column(nullable=True)
    invitee_security: Mapped[str] = mapped_column(nullable=True)

    status: Mapped[str] = mapped_column(
        date_invitation_status_enum, server_default="pending"
    )
    closing_hour: Mapped[time] = mapped_column(nullable=True)
    menu_url: Mapped[time] = mapped_column(nullable=True)

    inviter: Mapped["User"] = relationship(
        "User", uselist=False, back_populates="sent_dates", foreign_keys=[inviter_id]
    )
    invitee: Mapped["User"] = relationship(
        "User",
        uselist=False,
        back_populates="received_dates",
        foreign_keys=[invitee_id],
    )


class Booking(ModelMixin, Base):
    """
    Represents individual bookings for places.
    """

    __tablename__ = "bookings"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    place_id: Mapped[str] = mapped_column(ForeignKey("places.id", ondelete="CASCADE"))
    booking_type: Mapped[str] = mapped_column()
    booking_date: Mapped[datetime] = mapped_column()
    status: Mapped[str] = mapped_column(server_default="pending")
    user: Mapped["User"] = relationship("User", back_populates="bookings")
    place: Mapped["Place"] = relationship("Place", back_populates="bookings")
