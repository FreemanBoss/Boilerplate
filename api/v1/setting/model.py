from sqlalchemy import Boolean, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


from api.database.database import Base, ModelMixin

class Setting(ModelMixin, Base):
    """
    Represents the settings table in the database.
    """
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=False, index=True
    )
    language: Mapped[str] = mapped_column(String(5), default="en")
    dark_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    voice_call: Mapped[bool] = mapped_column(Boolean, default=True)
    video_call: Mapped[bool] = mapped_column(Boolean, default=True)
    notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    anonymous_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    travel_mode: Mapped[bool] = mapped_column(Boolean, default=False)


    # Relationships
    user = relationship("User", back_populates="settings")
