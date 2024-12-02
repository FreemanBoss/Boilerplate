from typing import TYPE_CHECKING
from sqlalchemy.orm import (
    mapped_column,
    Mapped,
    relationship
)
from sqlalchemy import ForeignKey

from api.database.database import Base, ModelMixin
from api.v1.reel.model import Reel
from api.v1.comment.model import (
        ProductComment,
        PhotoComment,
        ReelComment
    )

if TYPE_CHECKING:
    from api.v1.user.model import User


class ReelLike(ModelMixin, Base):
    """
    Represents reel_likes table in the database.
    """
    __tablename__ = "reel_likes"
    liker_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    reel_id: Mapped[str] = mapped_column(
        ForeignKey("reels.id", ondelete="SET NULL"), index=True,
    )

    liker: Mapped["User"] = relationship(
        "User", back_populates="reel_likes", foreign_keys=[liker_id]
    )
    reel: Mapped["Reel"] = relationship(
        "Reel", back_populates="likes", foreign_keys=[reel_id]
    )


class ReelCommentLike(ModelMixin, Base):
    """
    Represents reel_comment_likes table in the database.
    """
    __tablename__ = "reel_comment_likes"
    liker_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    reel_comment_id: Mapped[str] = mapped_column(
        ForeignKey("reel_comments.id", ondelete="SET NULL"), index=True,
    )

    liker: Mapped["User"] = relationship(
        "User", back_populates="reel_comment_likes", foreign_keys=[liker_id]
    )
    reel_comment: Mapped["ReelComment"] = relationship(
        "ReelComment", back_populates="likes", foreign_keys=[reel_comment_id]
    )


class PhotoLike(ModelMixin, Base):
    """
    Represents photo_likes table in the database.
    """
    __tablename__ = "photo_likes"
    liker_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    photo_id: Mapped[str] = mapped_column(
        ForeignKey("photos.id", ondelete="SET NULL"), index=True,
    )

    liker: Mapped["User"] = relationship(
        "User", back_populates="photo_likes", foreign_keys=[liker_id]
    )
    photo: Mapped["Photo"] = relationship(
        "Photo", back_populates="likes", foreign_keys=[photo_id]
    )


class PhotoCommentLike(ModelMixin, Base):
    """
    Represents photo_comment_likes table in the database.
    """
    __tablename__ = "photo_comment_likes"
    liker_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    photo_comment_id: Mapped[str] = mapped_column(
        ForeignKey("photo_comments.id", ondelete="SET NULL"), index=True,
    )

    liker: Mapped["User"] = relationship(
        "User", back_populates="photo_comment_likes", foreign_keys=[liker_id]
    )
    photo_comment: Mapped["PhotoComment"] = relationship(
        "PhotoComment", back_populates="likes", foreign_keys=[photo_comment_id]
    )


class ProductLike(ModelMixin, Base):
    """
    Represents product_likes table in the database.
    """
    __tablename__ = "product_likes"
    liker_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), index=True,
    )

    liker: Mapped["User"] = relationship(
        "User", back_populates="product_likes", foreign_keys=[liker_id]
    )
    product: Mapped["Product"] = relationship(
        "Product", back_populates="likes", foreign_keys=[product_id]
    )
    

class ProductCommentLike(ModelMixin, Base):
    """
    Represents product_comment_likes table in the database.
    """
    __tablename__ = "product_comment_likes"
    liker_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    product_comment_id: Mapped[str] = mapped_column(
        ForeignKey("product_comments.id", ondelete="SET NULL"), index=True,
    )

    liker: Mapped["User"] = relationship(
        "User", back_populates="product_comment_likes", foreign_keys=[liker_id]
    )
    product_comment: Mapped["ProductComment"] = relationship(
        "ProductComment", back_populates="likes", foreign_keys=[product_comment_id]
    )
