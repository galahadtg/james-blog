"""Role and Permission models for authorization.

Roles group permissions together. Users are assigned a single role.
Permissions define specific actions (e.g., 'post.create', 'user.delete').
"""

from sqlalchemy import String, Text, Table, Column, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


# Association table: Role <-> Permission (many-to-many)
role_permission = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


class Permission(Base):
    """A specific action that can be performed in the system.

    Permission codenames use dot notation: 'resource.action'
    Examples: post.create, post.publish, user.delete, admin.access
    """

    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    codename: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    roles = relationship("Role", secondary=role_permission, back_populates="permissions")

    def __repr__(self) -> str:
        return f"<Permission {self.codename}>"


class Role(TimestampMixin, Base):
    """A named group of permissions.

    Each user is assigned one role. The role determines what
    actions the user can perform in the system.
    """

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_system_role: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Relationships
    permissions = relationship(
        "Permission", secondary=role_permission, back_populates="roles", lazy="selectin"
    )
    users = relationship("User", back_populates="role", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Role {self.name}>"
