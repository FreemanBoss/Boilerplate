from typing import TYPE_CHECKING
from sqlalchemy import Numeric, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from api.database.database import Base, ModelMixin


if TYPE_CHECKING:
    from api.v1.user import User


class Wallet(ModelMixin, Base):
    """
    Represents the wallet table in the database.
    """
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete="SET NULL"), nullable=False)
    balance: Mapped[int] = mapped_column(Numeric(precision=10, scale=2), default=0.0, nullable=False)
    currency: Mapped[str] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship("User", uselist=False, back_populates="wallet")
