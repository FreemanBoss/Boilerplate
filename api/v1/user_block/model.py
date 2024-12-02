from typing import Optional
from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database.database import Base, ModelMixin, async_engine


class UserBlock(ModelMixin, Base):
    """
    Represents a user blocking another user in the database.
    """
    __tablename__ = "user_blocks"
    
    blocker_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    blocked_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    reason: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Relationships
    blocker = relationship("User", foreign_keys=[blocker_id], back_populates="blocked_users")
    blocked = relationship("User", foreign_keys=[blocked_id], back_populates="blocked_by")
    
    __table_args__ = (
        UniqueConstraint('blocker_id', 'blocked_id', name='uq_user_blocks'),
    )