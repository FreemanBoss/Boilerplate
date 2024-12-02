from typing import TYPE_CHECKING, List
from sqlalchemy.orm import (
    mapped_column,
    Mapped,
    relationship
)
from sqlalchemy import ForeignKey

from api.database.database import Base, ModelMixin
from api.v1.product.model import Product
from api.v1.reel.model import Reel
from api.v1.photo.model import Photo

if TYPE_CHECKING:
    from api.v1.user.model import User
    from api.v1.like.model import (
        ProductCommentLike,
        PhotoCommentLike,
        ReelCommentLike,
    )


# Dedicated comment table for low-traffic entity (Product)
class ProductComment(ModelMixin, Base):
    """
    Represents product_comments table in the database.
    """
    __tablename__ = "product_comments"
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), index=True
    )
    commenter_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    comment_text: Mapped[str]
    
    product: Mapped["Product"] = relationship(
        "Product", uselist=False, back_populates="comments", foreign_keys=[product_id]
    )
    
    commenter: Mapped["User"] = relationship(
        "User", uselist=False, back_populates="product_comments", foreign_keys=[commenter_id]
    )
    
    likes: Mapped[List["ProductCommentLike"]] = relationship(
        "ProductCommentLike", back_populates="product_comment"
    )


# Dedicated comment table for high-traffic entity (Reel)
class ReelComment(ModelMixin, Base):
    """
    Represents reel_comments table in the database.
    """
    __tablename__ = "reel_comments"
    reel_id: Mapped[str] = mapped_column(
        ForeignKey("reels.id", ondelete="SET NULL"), index=True
    )
    commenter_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    comment_text: Mapped[str]
    
    reel: Mapped["Reel"] = relationship(
        "Reel", uselist=False, back_populates="comments", foreign_keys=[reel_id]
    )
    
    commenter: Mapped["User"] = relationship(
        "User", uselist=False, back_populates="reel_comments", foreign_keys=[commenter_id]
    )
    
    likes: Mapped[List["ReelCommentLike"]] = relationship(
        "ReelCommentLike", back_populates="reel_comment"
    )


# Dedicated comment table for high-traffic entity (Photo)
class PhotoComment(ModelMixin, Base):
    """
    Represents photo_comments table in the database.
    """
    __tablename__ = "photo_comments"
    photo_id: Mapped[str] = mapped_column(
        ForeignKey("photos.id", ondelete="SET NULL"), index=True
    )
    commenter_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    comment_text: Mapped[str]
    
    photo: Mapped["Photo"] = relationship(
        "Photo", uselist=False, back_populates="comments", foreign_keys=[photo_id]
    )
    
    commenter: Mapped["User"] = relationship(
        "User", uselist=False, back_populates="photo_comments", foreign_keys=[commenter_id]
    )
    
    likes: Mapped[List["PhotoCommentLike"]] = relationship(
        "PhotoCommentLike", back_populates="photo_comment"
    )
