from typing import TYPE_CHECKING
from sqlalchemy import Numeric, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from api.database.database import Base, ModelMixin
from api.v1.events.model import EventTicket

if TYPE_CHECKING:
    from api.v1.user.model import User



class Payment(ModelMixin, Base):
    """`
    Represents the payments table in the database.
    """
    payer_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete="SET NULL"), nullable=False)

    transaction_id: Mapped[str] = mapped_column(nullable=True, comment="The ID returned by the payment gateway")
    payer: Mapped[str] = mapped_column(nullable=False, comment="User, admin, superadmin")
    payment_for: Mapped[str] = mapped_column(nullable=False, comment="Product, fund wallet, etc.")
    amount: Mapped[str] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    currency: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False, comment="Status of the payment: failed, pending, success")
    payment_provider: Mapped[str] = mapped_column(nullable=False, comment="Payment gateway used: stripe, paypal, flutterwave, paystack")


    payer_user: Mapped["User"] = relationship("User", back_populates="payments")
    event_ticket: Mapped["EventTicket"] = relationship("EventTicket", uselist=False, back_populates="payment")
