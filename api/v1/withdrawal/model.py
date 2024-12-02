from typing import TYPE_CHECKING
from sqlalchemy import Numeric, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from api.database.database import Base, ModelMixin


if TYPE_CHECKING:
    from api.v1.user.model import User

class Withdrawal(ModelMixin, Base):
    """
    Represents the Withdrawal table in the database.
    """
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete="SET NULL"), nullable=False)
    amount: Mapped[int] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    destination: Mapped[str]= mapped_column(nullable=True)
    destination_type: Mapped[str] = mapped_column(nullable=True)
    account_number: Mapped[str] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="withdrawals")
