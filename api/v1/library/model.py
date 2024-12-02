from typing import TYPE_CHECKING, Optional
from sqlalchemy.orm import (
    mapped_column,
    Mapped,
    relationship
)
from sqlalchemy import ForeignKey

from api.database.database import Base, ModelMixin

if TYPE_CHECKING:
    from api.v1.user.model import User


class Library(ModelMixin, Base):
    """
    Represents libraries table in the database.
    """
    __tablename__ = "libraries"
    creator_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    title: Mapped[str] = mapped_column(index=True)
    category: Mapped[str]
    cover_url: Mapped[Optional[str]] = mapped_column(nullable=True)
    book_url: Mapped[Optional[str]] = mapped_column(nullable=True)
    rating: Mapped[int]
    price: Mapped[Optional[float]] = mapped_column(nullable=True)
    
    creator: Mapped["User"] = relationship(
        "User", uselist=False, back_populates="libraries"
    )
