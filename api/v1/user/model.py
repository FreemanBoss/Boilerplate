from sqlalchemy.sql import func
from typing import Optional, List
from passlib.context import CryptContext
from sqlalchemy import Boolean, String, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timedelta, timezone


from api.database.database import Base, ModelMixin, async_engine


is_sqlite = async_engine.url.get_backend_name() == "sqlite"


data_type = JSON if is_sqlite else JSONB


from api.v1.setting.model import Setting
from api.v1.auth.model import PasswordResetToken
from api.v1.role_and_permission.model import Role, user_roles
from api.v1.profile.model import Profile
from api.v1.photo.model import Photo, ProfilePhoto
from api.v1.user_block.model import UserBlock
from api.v1.reel.model import Reel
from api.v1.activity_log.model import ActivityLog
from api.v1.user_device.model import UserDevice
from api.v1.date_invitation.model import DateInvitation, Booking
from api.v1.library.model import Library
from api.v1.location.model import UserLocation
from api.v1.subscriptions.model import SubscriptionPlan, Subscription
from api.v1.notification.model import Notification, PushNotification
from api.v1.match.model import Match
from api.v1.place.model import Place
from api.v1.withdrawal.model import Withdrawal
from api.v1.user_exit_feedback.model import UserExitFeedback
from api.v1.verification_request.model import VerificationRequest
from api.v1.sticker.model import ExchangedSticker, Sticker
from api.v1.gift.model import ExchangedGift, Gift
from api.v1.product.model import Product
from api.v1.wallet.model import Wallet
from api.v1.payments.model import Payment
from api.v1.dyt_token.model import DytToken
from api.v1.events.model import Event, EventTicket
from api.v1.trusted_devices.model import TrustedDevice
from api.v1.like.model import (
    PhotoCommentLike,
    ProductCommentLike,
    ReelCommentLike,
    PhotoLike,
    ReelLike,
    ProductLike,
)
from api.v1.comment.model import (
    ProductComment,
    PhotoComment,
    ReelComment,
)


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(ModelMixin, Base):
    """
    Represents users table in the database.
    """

    password: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    first_name: Mapped[Optional[str]] = mapped_column(String(50))
    last_name: Mapped[Optional[str]] = mapped_column(String(50))
    two_factor_secret: Mapped[str] = mapped_column(String(255), nullable=True)
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    backup_codes: Mapped[List[str]] = mapped_column(data_type, nullable=True)
    two_factor_enabled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    email_verified: Mapped[bool] = mapped_column(Boolean, default=True)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    is_suspended: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login = mapped_column(DateTime(timezone=True), server_default=func.now())
    secret_token_identifier: Mapped[str] = mapped_column(nullable=True)

    # Relationships
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="user", passive_deletes=True
    )
    push_notifications: Mapped[List["PushNotification"]] = relationship(
        "PushNotification", back_populates="user", passive_deletes=True
    )
    settings: Mapped["Setting"] = relationship(
        back_populates="user", passive_deletes=True
    )

    roles: Mapped[List["Role"]] = relationship(
        "Role",
        back_populates="users",
        secondary=user_roles,
        passive_deletes=True,
        lazy="joined",
    )

    profile_photos: Mapped[List["ProfilePhoto"]] = relationship(
        "ProfilePhoto", back_populates="user", passive_deletes=True
    )

    trusted_devices: Mapped[List["TrustedDevice"]] = relationship(
        "TrustedDevice", back_populates="user", passive_deletes=True
    )

    blocked_users: Mapped[List["UserBlock"]] = relationship(
        "UserBlock",
        foreign_keys=[UserBlock.blocker_id],
        back_populates="blocker",
        passive_deletes=True
    )
    blocked_by: Mapped[List["UserBlock"]] = relationship(
        "UserBlock",
        foreign_keys=[UserBlock.blocked_id],
        back_populates="blocked",
        passive_deletes=True
    )

    photos: Mapped[List["Photo"]] = relationship(
        "Photo", back_populates="user", passive_deletes=True
    )

    profile: Mapped["Profile"] = relationship(
        "Profile", uselist=False, back_populates="user", passive_deletes=True
    )

    products: Mapped[List["Product"]] = relationship(
        "Product", back_populates="creator", passive_deletes=True
    )

    product_comments: Mapped[List["ProductComment"]] = relationship(
        "ProductComment", back_populates="commenter", passive_deletes=True
    )
    reel_comments: Mapped[List["ReelComment"]] = relationship(
        "ReelComment", back_populates="commenter", passive_deletes=True
    )
    password_reset_tokens: Mapped["PasswordResetToken"] = relationship(
        "PasswordResetToken", back_populates="user", passive_deletes=True
    )
    photo_comments: Mapped[List["PhotoComment"]] = relationship(
        "PhotoComment", back_populates="commenter", passive_deletes=True
    )
    withdrawals: Mapped[List["Withdrawal"]] = relationship(
        "Withdrawal", back_populates="user", passive_deletes=True
    )
    wallet: Mapped["Wallet"] = relationship(
        "Wallet", uselist=False, back_populates="user", passive_deletes=True
    )
    payments: Mapped[List["Payment"]] = relationship(
        "Payment", back_populates="payer_user", passive_deletes=True
    )
    dyt_tokens: Mapped["DytToken"] = relationship("DytToken", back_populates="user")
    product_likes: Mapped[List["ProductLike"]] = relationship(
        "ProductLike", back_populates="liker", passive_deletes=True
    )
    product_comment_likes: Mapped[List["ProductCommentLike"]] = relationship(
        "ProductCommentLike", back_populates="liker", passive_deletes=True
    )

    reel_likes: Mapped[List["ReelLike"]] = relationship(
        "ReelLike", back_populates="liker", passive_deletes=True
    )
    reel_comment_likes: Mapped[List["ReelCommentLike"]] = relationship(
        "ReelCommentLike", back_populates="liker", passive_deletes=True
    )

    photo_likes: Mapped[List["PhotoLike"]] = relationship(
        "PhotoLike", back_populates="liker", passive_deletes=True
    )
    photo_comment_likes: Mapped[List["PhotoCommentLike"]] = relationship(
        "PhotoCommentLike", back_populates="liker", passive_deletes=True
    )

    # all activities of a user
    activities: Mapped[List["ActivityLog"]] = relationship(
        "ActivityLog",
        back_populates="user",
        passive_deletes=True,
        foreign_keys=[ActivityLog.user_id],
    )

    # the other user the activity was targeted at
    target_activities: Mapped[List["ActivityLog"]] = relationship(
        "ActivityLog",
        back_populates="target_user",
        passive_deletes=True,
        foreign_keys=[ActivityLog.target_user_id],
    )
    bookings: Mapped[List["Booking"]] = relationship("Booking", back_populates="user",
        passive_deletes=True, foreign_keys=[Booking.user_id])

    sent_dates: Mapped[List["DateInvitation"]] = relationship(
        "DateInvitation",
        back_populates="inviter",
        passive_deletes=True,
        foreign_keys=[DateInvitation.inviter_id],
    )
    received_dates: Mapped[List["DateInvitation"]] = relationship(
        "DateInvitation",
        back_populates="invitee",
        passive_deletes=True,
        foreign_keys=[DateInvitation.invitee_id],
    )

    sent_gists: Mapped[List["ExchangedGift"]] = relationship(
        "ExchangedGift",
        back_populates="sender",
        passive_deletes=True,
        foreign_keys=[ExchangedGift.sender_id],
    )
    received_gifts: Mapped[List["ExchangedGift"]] = relationship(
        "ExchangedGift",
        back_populates="receiver",
        passive_deletes=True,
        foreign_keys=[ExchangedGift.receiver_id],
    )
    created_gifts: Mapped[List["Gift"]] = relationship(
        "Gift",
        back_populates="creator",
        passive_deletes=True,
    )
    event_tickets: Mapped[List["EventTicket"]] = relationship(
        "EventTicket", back_populates="user", passive_deletes=True
    )
    events: Mapped[List["Event"]] = relationship(
        "Event", back_populates="creator", passive_deletes=True
    )

    libraries: Mapped[List["Library"]] = relationship(
        "Library", back_populates="creator", passive_deletes=True
    )

    locations: Mapped[List["UserLocation"]] = relationship(
        "UserLocation", back_populates="user", passive_deletes=True
    )
    dyt_tokens = relationship("DytToken", back_populates="user")

    sent_matches: Mapped[List["Match"]] = relationship(
        "Match",
        back_populates="user_sent_match",
        passive_deletes=True,
        foreign_keys=[Match.user_sent_match_id],
    )
    accepted_matches: Mapped[List["Match"]] = relationship(
        "Match",
        back_populates="user_accept_match",
        passive_deletes=True,
        foreign_keys=[Match.user_accept_match_id],
    )

    places: Mapped[List["Place"]] = relationship(
        "Place", back_populates="creator", passive_deletes=True
    )

    reel: Mapped[List["Reel"]] = relationship(
        "Reel", back_populates="creator", passive_deletes=True
    )

    sent_stickers: Mapped[List["ExchangedSticker"]] = relationship(
        "ExchangedSticker",
        back_populates="sender",
        passive_deletes=True,
        foreign_keys=[ExchangedSticker.sender_id],
    )
    received_stickers: Mapped[List["ExchangedSticker"]] = relationship(
        "ExchangedSticker",
        back_populates="receiver",
        passive_deletes=True,
        foreign_keys=[ExchangedSticker.receiver_id],
    )

    created_stickers: Mapped[List["Sticker"]] = relationship(
        "Sticker", back_populates="creator", passive_deletes=True
    )

    user_exit_feedbacks: Mapped[List["UserExitFeedback"]] = relationship(
        "UserExitFeedback", back_populates="exiting_user", passive_deletes=True
    )

    sent_verification_request: Mapped["VerificationRequest"] = relationship(
        "VerificationRequest",
        uselist=False,
        back_populates="user_to_verify",
        passive_deletes=True,
        foreign_keys=[VerificationRequest.user_to_verify_id],
    )

    verification_requests: Mapped[List["VerificationRequest"]] = relationship(
        "VerificationRequest",
        back_populates="verifier",
        passive_deletes=True,
        foreign_keys=[VerificationRequest.verifier_id],
    )

    user_devices: Mapped[List["UserDevice"]] = relationship(
        "UserDevice", back_populates="user", passive_deletes=True
    )

    subscription_plans: Mapped[List["SubscriptionPlan"]] = relationship(
        "SubscriptionPlan", uselist=False, back_populates="creator"
    )

    subscriptions: Mapped["Subscription"] = relationship(
        "Subscription", uselist=False, back_populates="subscriber"
    )

    def to_dict(self) -> dict:
        obj_dict = super().to_dict()
        obj_dict.pop("password", None)
        if self.last_login:
            obj_dict["last_login"] = self.last_login.isoformat()
        return obj_dict

    def update_last_login(self):
        """update user's last login field"""
        self.last_login = datetime.now(timezone(timedelta(hours=1)))

    def update_active_status(self):
        """update active based on last_login"""
        if self.last_login and isinstance(self.last_login, datetime):
            current_time = datetime.now(timezone(timedelta(hours=1)))
            one_hour_ago = current_time - timedelta(hours=1)

            if self.last_login.tzinfo is None:
                self.last_login = self.last_login.replace(
                    tzinfo=timezone(timedelta(hours=1))
                )

            self.is_active = self.last_login >= one_hour_ago

    def set_password(self, plain_password: str) -> None:
        """
        Sets a user password.


        Args:
            plain_password(str): password to hash.
        """
        if not plain_password or plain_password == "":
            return
        hashed_password = password_context.hash(plain_password)
        self.password = hashed_password

    def verify_password(self, plain_password) -> bool:
        """
        Verifies user password.


        Args:
            plain_password(str): password to compare with hash.
        """
        if not plain_password:
            raise Exception(f"{plain_password} must be provided")
        return password_context.verify(secret=plain_password, hash=self.password)

    def __str__(self):
        return self.email
