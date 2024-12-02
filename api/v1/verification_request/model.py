from typing import TYPE_CHECKING, Optional
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey

from api.database.database import Base, ModelMixin
from api.v1.enum_types import verification_status_enum

if TYPE_CHECKING:
    from api.v1.user.model import User


class VerificationRequest(ModelMixin, Base):
    """
    Represents verification_requests table in the database.
    """

    __tablename__ = "verification_requests"
    user_to_verify_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )  # indicating the user requesting verification.
    verifier_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )  # indicating the admin who verifies the user.

    status: Mapped[str] = mapped_column(
        verification_status_enum
    )  # indicating the status of the verification request

    verified_by_bot: Mapped[bool] = mapped_column(
        server_default="FALSE",
    )
    verifier_feedback: Mapped[str] = mapped_column(nullable=True)
    photo_url: Mapped[str]

    verification_count: Mapped[int] = mapped_column(default=0)

    user_to_verify: Mapped["User"] = relationship(
        "User",
        uselist=False,
        back_populates="sent_verification_request",
        foreign_keys=[user_to_verify_id],
    )
    verifier: Mapped["User"] = relationship(
        "User",
        uselist=False,
        back_populates="verification_requests",
        foreign_keys=[verifier_id],
    )
