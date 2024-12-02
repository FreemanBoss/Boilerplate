from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, String, DateTime

from api.database.database import Base, ModelMixin
from api.v1.enum_types import subscription_plans_enum, subscription_status_enum

if TYPE_CHECKING:
    from api.v1.user.model import User


class SubscriptionPlan(ModelMixin, Base):
    """
    Represents subscription_plans table in the database.
    """

    __tablename__ = "subscription_plans"
    creator_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(index=True)
    duration: Mapped[str] = mapped_column(subscription_plans_enum)
    amount: Mapped[float] = mapped_column(default=0.0, nullable=True)
    price: Mapped[float] = mapped_column(default=0.0, nullable=True)
    banner_url: Mapped[str] = mapped_column(String(255), nullable=True)

    creator: Mapped["User"] = relationship(
        "User", uselist=False, back_populates="subscription_plans"
    )
    subscription: Mapped["Subscription"] = relationship(
        "Subscription", uselist=False, back_populates="subscription_plan"
    )


class Subscription(ModelMixin, Base):
    """
    Represents subscriptions table in the database.
    """

    subscriber_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    subscription_plan_id: Mapped[str] = mapped_column(
        ForeignKey("subscription_plans.id", ondelete="SET NULL"),
    )
    expires_in: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[str] = mapped_column(
        subscription_status_enum, server_default="active"
    )

    subscriber: Mapped["User"] = relationship(
        "User", uselist=False, back_populates="subscriptions"
    )
    subscription_plan: Mapped["SubscriptionPlan"] = relationship(
        "SubscriptionPlan", uselist=False, back_populates="subscription"
    )
