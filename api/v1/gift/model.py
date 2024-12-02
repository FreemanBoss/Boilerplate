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


class Gift(ModelMixin, Base):
    """
    Represents gifts table in the database.
    """
    creator_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    name: Mapped[str] = mapped_column(index=True)
    currency: Mapped[str]
    price: Mapped[float]
    
    creator: Mapped["User"] = relationship(
        "User", uselist=False, back_populates="created_gifts"
    )
    exchanged_gifts: Mapped[list["ExchangedGift"]] = relationship(
        "ExchangedGift", back_populates="gift"
    )


class ExchangedGift(ModelMixin, Base):
    """
    Represents exchanged_gifts table in the database.
    """
    __tablename__ = "received_gifts"
    sender_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    receiver_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    gift_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("gifts.id", ondelete="SET NULL"), nullable=True
    )
    
    sender: Mapped["User"] = relationship(
        "User", uselist=False, back_populates="sent_gists", foreign_keys=[sender_id]
    )
    receiver: Mapped["User"] = relationship(
        "User", uselist=False, back_populates="received_gifts", foreign_keys=[receiver_id]
    )
    gift: Mapped["Gift"] = relationship(
        "Gift", uselist=False, back_populates="exchanged_gifts",  foreign_keys=[gift_id]
    )
