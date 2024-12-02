from typing import TYPE_CHECKING, List
from datetime import time
from sqlalchemy.orm import (
    mapped_column,
    Mapped,
    relationship,
    validates,
)
from sqlalchemy import ForeignKey, TIME
from sqlalchemy import ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB

from api.database.database import Base, ModelMixin, async_engine

if TYPE_CHECKING:
    from api.v1.user.model import User
    from api.v1.location.model import PlaceLocation
    from api.v1.date_invitation.model import Booking

is_sqlite = async_engine.url.get_backend_name() == "sqlite"

# i am using sqlite for tests, since sqlite does not support  JSONB,
# conditionally using JSON
data_type = JSON if is_sqlite else JSONB


class Place(ModelMixin, Base):
    """
    Represents stickers table in the database.
    """

    creator_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    name: Mapped[str]
    category_id: Mapped[str] = mapped_column(
        ForeignKey("place_categories.id", ondelete="SET NULL")
    )

    banner: Mapped[dict] = mapped_column(data_type)
    rating: Mapped[int] = mapped_column(nullable=True)
    opening_hour: Mapped[time] = mapped_column(
        TIME, nullable=True, default=lambda: time(9, 00)
    )
    about: Mapped[str]
    closing_hour: Mapped[time] = mapped_column(
        TIME, nullable=True, default=lambda: time(21, 00)
    )
    menu_url: Mapped[str] = mapped_column(nullable=True)

    creator: Mapped["User"] = relationship(
        "User", uselist=False, back_populates="places"
    )
    category: Mapped["PlaceCategory"] = relationship(
        "PlaceCategory", uselist=False, back_populates="places"
    )
    locations: Mapped[List["PlaceLocation"]] = relationship(
        "PlaceLocation", uselist=False, back_populates="place"
    )
    bookings: Mapped[List["Booking"]] = relationship("Booking", back_populates="place")

    @validates("closing_hour")
    def validate_closing_time(self, key, value):
        """
        Validate closing_hour against opening_hour.
        """
        if value <= self.opening_hour:
            raise ValueError("Closing hour must be after opening time.")
        return value


class PlaceCategory(ModelMixin, Base):
    """
    Represents stickers table in the database.
    """

    __tablename__ = "place_categories"
    name: Mapped[str]
    places: Mapped["Place"] = relationship(
        "Place", back_populates="category", passive_deletes=True
    )
