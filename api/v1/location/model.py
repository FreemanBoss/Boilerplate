from typing import TYPE_CHECKING, List
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey

from api.database.database import Base, ModelMixin

if TYPE_CHECKING:
    from api.v1.user.model import User
    from api.v1.place.model import Place
    from api.v1.events.model import Event


class Location(ModelMixin, Base):
    """
    Represents locations table in the database.
    """

    city: Mapped[str] = mapped_column(nullable=True)
    state: Mapped[str] = mapped_column(nullable=True)
    country: Mapped[str] = mapped_column(nullable=True)
    latitued: Mapped[float] = mapped_column(nullable=True)
    longitude: Mapped[float] = mapped_column(nullable=True)

    users: Mapped[List["UserLocation"]] = relationship(
        "UserLocation",
        back_populates="location",
        passive_deletes=True,
    )
    places: Mapped[List["PlaceLocation"]] = relationship(
        "PlaceLocation",
        back_populates="location",
        passive_deletes=True,
    )
    events: Mapped[List["EventLocation"]] = relationship(
        "EventLocation",
        back_populates="location",
        passive_deletes=True,
    )


class UserLocation(ModelMixin, Base):
    """
    Represents user_locations table in the database.
    """

    __tablename__ = "user_locations"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    location_id: Mapped[str] = mapped_column(
        ForeignKey("locations.id", ondelete="SET NULL")
    )
    is_current: Mapped[bool] = mapped_column(default=True)

    user: Mapped["User"] = relationship(
        "User", back_populates="locations", passive_deletes=True
    )
    location: Mapped["Location"] = relationship(
        "Location", back_populates="users", passive_deletes=True
    )


class PlaceLocation(ModelMixin, Base):
    """
    Represents place_locations table in the database.
    """

    __tablename__ = "place_locations"

    place_id: Mapped[str] = mapped_column(ForeignKey("places.id", ondelete="SET NULL"))
    location_id: Mapped[str] = mapped_column(
        ForeignKey("locations.id", ondelete="SET NULL")
    )
    is_current: Mapped[bool] = mapped_column(default=True)

    place: Mapped["Place"] = relationship(
        "Place", back_populates="locations", passive_deletes=True
    )
    location: Mapped["Location"] = relationship(
        "Location", back_populates="places", passive_deletes=True
    )


class EventLocation(ModelMixin, Base):
    """
    Represents event_locations table in the database.
    """

    __tablename__ = "event_locations"

    event_id: Mapped[str] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"))
    location_id: Mapped[str] = mapped_column(
        ForeignKey("locations.id", ondelete="SET NULL")
    )
    is_current: Mapped[bool] = mapped_column(default=True)

    event: Mapped["Event"] = relationship(
        "Event", back_populates="locations", passive_deletes=True
    )
    location: Mapped["Location"] = relationship(
        "Location", back_populates="events", passive_deletes=True
    )

    def __repr__(self):
        return f"<EventLocation(city={self.city}, state={self.state}, country={self.country})>"
