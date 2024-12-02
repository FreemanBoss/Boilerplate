from typing import TYPE_CHECKING, List
from datetime import datetime
from sqlalchemy import String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from api.database.database import Base, ModelMixin


if TYPE_CHECKING:
    from api.v1.user.model import User
    from api.v1.payments.model import Payment
    from api.v1.location.model import EventLocation


class Event(ModelMixin, Base):
    """
    Represents the events table in the database.
    """
    creator_id: Mapped[str] = mapped_column(String, ForeignKey('users.id', ondelete="SET NULL"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=True)
    details: Mapped[str] = mapped_column(Text, nullable=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    location: Mapped[str] = mapped_column(String, nullable=True)
    ticket_price: Mapped[str] = mapped_column(Numeric(precision=10, scale=2), nullable=True)
    banner: Mapped[str] = mapped_column(String, nullable=True)  # URL or path to the banner image
    tickets_available: Mapped[int] = mapped_column(nullable=True)
    total_capacity: Mapped[int] = mapped_column(nullable=True)
    ticket_types: Mapped[str] = mapped_column(nullable=False, default="regular")
    creator: Mapped["User"] = relationship("User", uselist=False, back_populates="events")
    locations: Mapped[List["EventLocation"]] = relationship("EventLocation", back_populates="event", passive_deletes=True)
    tickets: Mapped[List["EventTicket"]] = relationship("EventTicket", back_populates="event", passive_deletes=True)


class EventTicket(ModelMixin, Base):
    """
    Represents the event_tickets table in the database.
    """
    __tablename__ = "event_tickets"
    event_id: Mapped[str] = mapped_column(String, ForeignKey('events.id', ondelete="SET NULL"), nullable=False)
    location_id: Mapped[str] = mapped_column(
        ForeignKey("event_locations.id", ondelete="SET NULL")
    )
    user_id: Mapped[str] = mapped_column(String, ForeignKey('users.id', ondelete="SET NULL"), nullable=False)
    payment_id: Mapped[str] = mapped_column(
        ForeignKey('payments.id', ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(default="reserved")

    ticket_price: Mapped[str] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    quantity: Mapped[int] = mapped_column(default=1, nullable=False)
    ticket_type: Mapped[str] = mapped_column(String, default="regular", nullable=False)

    event: Mapped["Event"] = relationship("Event", uselist=False, back_populates="tickets")
    user: Mapped["User"] = relationship("User", uselist=False, back_populates="event_tickets")
    payment: Mapped["Payment"] = relationship("Payment", uselist=False, back_populates="event_ticket")
