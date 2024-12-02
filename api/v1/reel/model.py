from typing import TYPE_CHECKING, List
from sqlalchemy.orm import (
    mapped_column,
    Mapped,
    relationship
)
from sqlalchemy import ForeignKey

from api.database.database import Base, ModelMixin


if TYPE_CHECKING:
    from api.v1.user.model import User
    from api.v1.comment.model import ReelComment
    from api.v1.like.model import ReelLike


class Reel(ModelMixin, Base):
    """
    Represents reels table in the database.
    """
    creator_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )  # indicating the admin user creating the reel.
    url: Mapped[str]

    creator: Mapped["User"] = relationship(
        "User", uselist=False, back_populates="reel", foreign_keys=[creator_id]
    )
    
    likes: Mapped[List["ReelLike"]] = relationship(
        "ReelLike", back_populates="reel", passive_deletes=True
    )
    comments: Mapped[List["ReelComment"]] = relationship(
        "ReelComment", back_populates="reel", passive_deletes=True
    )

