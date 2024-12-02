from typing import TYPE_CHECKING
from sqlalchemy import Numeric, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from api.database.database import ModelMixin, Base

if TYPE_CHECKING:
    from api.v1.user.model import User

class DytToken(ModelMixin, Base):
    """
    Represents the dytokens table in the database.
    """
    __tablename__ = "dyt_tokens"
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete="SET NULL"), nullable=False)
    balance: Mapped[str] = mapped_column(Numeric(precision=10, scale=2), default=0.0)

    user: Mapped["User"] = relationship("User", back_populates="dyt_tokens")
