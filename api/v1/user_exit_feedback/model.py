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


class UserExitFeedback(ModelMixin, Base):
    """
    Represents user_exit_feedback table in the database.
    """
    __tablename__ = "user_exit_feedbacks"
    exiting_user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    reason: Mapped[str]
    additional_feedback: Mapped[Optional[str]] = mapped_column(nullable=True)
    
    exiting_user: Mapped["User"] = relationship(
        "User", uselist=False, back_populates="user_exit_feedbacks", foreign_keys=[exiting_user_id]
    )
