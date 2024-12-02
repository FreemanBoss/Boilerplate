from typing import Optional
from typing import Optional
from sqlalchemy import Boolean, String, JSON, DateTime, Enum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from sqlalchemy import ForeignKey


from api.database.database import Base, ModelMixin, async_engine
from api.v1.enum_types import gender_type_enum, genotype_enum, joining_purpose_enum

is_sqlite = async_engine.url.get_backend_name() == "sqlite"


data_type = JSON if is_sqlite else JSONB


class Profile(ModelMixin, Base):
    """
    Represents profiles table in the database.
    """

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    recovery_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    phone: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    height: Mapped[Optional[str]] = mapped_column(nullable=True)
    genotype: Mapped[str] = mapped_column(
        genotype_enum,
        nullable=True,
    )
    last_active_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    gender: Mapped[str] = mapped_column(
        gender_type_enum,
        nullable=True,
    )
    date_of_birth: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    location: Mapped[Optional[dict]] = mapped_column(data_type, nullable=True)

    # Relationships
    user = relationship("User", uselist=False, back_populates="profile")
    preferences = relationship(
        "ProfilePreference",
        back_populates="profile",
        uselist=False,
        passive_deletes=True,
    )
    traits = relationship(
        "ProfileTrait", back_populates="profile", uselist=False, passive_deletes=True
    )

    __table_args__ = (Index("idx_profile_user_id", "user_id"),)


class ProfilePreference(ModelMixin, Base):
    """
    Represents profile_preferences table in the database.
    """

    __tablename__ = "profile_preferences"
    profile_id: Mapped[str] = mapped_column(
        ForeignKey("profiles.id", ondelete="SET NULL"), nullable=False, index=True
    )
    joining_purpose: Mapped[str] = mapped_column(
        joining_purpose_enum,
        nullable=True,
    )
    preferred_gender: Mapped[Optional[str]] = mapped_column(
        gender_type_enum,
        nullable=True,
    )
    desired_relationship: Mapped[Optional[list[str]]] = mapped_column(
    data_type, nullable=True
    )
    ideal_partner_qualities: Mapped[Optional[dict]] = mapped_column(
        data_type, nullable=True
    )
    lifestyle_habits: Mapped[Optional[list[str]]] = mapped_column(data_type, nullable=True)
    family_plans: Mapped[Optional[dict]] = mapped_column(data_type, nullable=True)
    religion: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    political_views: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    location_preference: Mapped[Optional[dict]] = mapped_column(
        data_type, nullable=True
    )
    age_range: Mapped[Optional[dict]] = mapped_column(data_type, nullable=True)
    distance_range: Mapped[Optional[dict]] = mapped_column(data_type, nullable=True)

    # Relationships
    profile = relationship("Profile", back_populates="preferences")


class ProfileTrait(ModelMixin, Base):
    """
    Represents profile_traits table in the database.
    """

    __tablename__ = "profile_traits"
    profile_id: Mapped[str] = mapped_column(
        ForeignKey("profiles.id", ondelete="SET NULL"), nullable=False, index=True
    )
    hobbies: Mapped[Optional[list[str]]] = mapped_column(data_type, nullable=True)
    habits: Mapped[Optional[list[str]]] = mapped_column(data_type, nullable=True)

    # Relationships
    profile = relationship("Profile", back_populates="traits")
