from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional
from api.database.database import Base, ModelMixin
if TYPE_CHECKING:
    from api.v1.user.model import User


class PasswordResetToken(ModelMixin, Base):
    __tablename__ = "password_reset_tokens"

    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"),
                        unique=True)
    jti: Mapped[str] = mapped_column(String)
    
    user: Mapped["User"] = relationship("User", back_populates="password_reset_tokens")

    def is_expired(self):
        return datetime.utcnow() > self.created_at + timedelta(minutes=10)
