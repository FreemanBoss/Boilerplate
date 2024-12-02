from typing import TYPE_CHECKING
from typing import Optional
from sqlalchemy import Boolean, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


from api.database.database import Base, ModelMixin


if  TYPE_CHECKING:
    from api.v1.comment.model import PhotoComment
    from api.v1.like.model import PhotoLike    


class Photo(ModelMixin, Base):
    """
    Represents photos table in the database.
    """
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=False, index=True
    )
    chat_id: Mapped[Optional[str]] = mapped_column(nullable=True, index=True)
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), index=True, nullable=True
    )
    linked_to: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Possible values: 'profile', 'chat'
    url: Mapped[str] = mapped_column(String, nullable=False)
    is_profile_picture: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)


    # Relationships
    user = relationship("User", back_populates="photos")
   
    comments: Mapped["PhotoComment"] = relationship(
        "PhotoComment", back_populates="photo", passive_deletes=True
    )
   
    likes: Mapped["PhotoLike"] = relationship(
        "PhotoLike", back_populates="photo", passive_deletes=True
    )

class ProfilePhoto(ModelMixin, Base):
    """
    Represents a user's profile photos in the database.
    """

    __tablename__ = "profile_photos"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    url: Mapped[str] = mapped_column(String, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    user = relationship("User", back_populates="profile_photos")

