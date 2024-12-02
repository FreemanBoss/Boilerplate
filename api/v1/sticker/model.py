from typing import TYPE_CHECKING
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey

from api.database.database import Base, ModelMixin

if TYPE_CHECKING:
    from api.v1.user.model import User


class Sticker(ModelMixin, Base):
    """
    Represents stickers table in the database.
    """

    creator_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    name: Mapped[str] = mapped_column(index=True)
    currency: Mapped[str]
    price: Mapped[float]
    url: Mapped["str"]

    creator: Mapped["User"] = relationship(
        "User", uselist=False, back_populates="created_stickers"
    )
    exchanged_stickers: Mapped[list["ExchangedSticker"]] = relationship(
        "ExchangedSticker", back_populates="sticker", passive_deletes=True
    )


class ExchangedSticker(ModelMixin, Base):
    """
    Represents exchanged_stickers table in the database.
    """

    __tablename__ = "exchanged_stickers"
    sender_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    receiver_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    sticker_id: Mapped[str] = mapped_column(
        ForeignKey("stickers.id", ondelete="SET NULL"), nullable=True
    )
    quantity: Mapped[int] = mapped_column(default=1, nullable=True)

    sender: Mapped["User"] = relationship(
        "User", uselist=False, back_populates="sent_stickers", foreign_keys=[sender_id]
    )
    receiver: Mapped["User"] = relationship(
        "User",
        uselist=False,
        back_populates="received_stickers",
        foreign_keys=[receiver_id],
    )
    sticker: Mapped["Sticker"] = relationship(
        "Sticker",
        uselist=False,
        back_populates="exchanged_stickers",
        foreign_keys=[sticker_id],
    )
