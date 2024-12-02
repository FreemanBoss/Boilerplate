from typing import TYPE_CHECKING
from sqlalchemy.orm import (
    mapped_column,
    Mapped,
    relationship
)
from sqlalchemy import ForeignKey

from api.database.database import Base, ModelMixin

if TYPE_CHECKING:
    from api.v1.user.model import User


class Match(ModelMixin, Base):
    """
    Represents matches table in the database.
    """
    __tablename__ = "matches"
    user_sent_match_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    user_accept_match_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )

    relationship_type: Mapped[str] = mapped_column(nullable=True)  # indicating the type of relationship (e.g., dating, love, marriage).
    notify: Mapped[bool] = mapped_column(server_default="FALSE")  # indicating if notifications are enabled for the match.
    
    user_sent_match: Mapped["User"] = relationship(
        "User", uselist=False, back_populates="sent_matches", foreign_keys=[user_sent_match_id]
    )
    user_accept_match: Mapped["User"] = relationship(
        "User", uselist=False, back_populates="accepted_matches", foreign_keys=[user_accept_match_id]
    )
