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
    from api.v1.comment.model import ProductComment
    from api.v1.like.model import ProductLike
    


class Product(ModelMixin, Base):
    """
    Represents products table in the database.
    """
    creator_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
    )
    
    creator: Mapped["User"] = relationship(
        "User", uselist=False, back_populates="products", foreign_keys=[creator_id]
    )
    
    comments: Mapped["ProductComment"] = relationship(
        "ProductComment", back_populates="product", passive_deletes=True,
    )
    
    likes: Mapped["ProductLike"] = relationship(
        "ProductLike", back_populates="product", passive_deletes=True,
    )
