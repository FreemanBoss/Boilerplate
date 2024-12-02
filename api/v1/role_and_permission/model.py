from typing import TYPE_CHECKING, List
from sqlalchemy import Column, String, Table, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from api.database.database import Base, ModelMixin


if TYPE_CHECKING:
    from api.v1.user.model import User


role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column(
        "role_id", String, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "permission_id",
        String,
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


user_roles = Table(
    "user_roles",
    Base.metadata,
    Column(
        "user_id", String, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "role_id", String, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    ),
)


class Role(ModelMixin, Base):
    """
    Represents the role table in the database.
    """

    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String)

    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin",
        passive_deletes=True,
    )
    users: Mapped[List["User"]] = relationship(
        "User", secondary=user_roles, back_populates="roles", passive_deletes=True
    )


class Permission(ModelMixin, Base):
    """
    Represents the permission table in the database.
    """

    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    description: Mapped[str]

    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions",
        passive_deletes=True,
    )
