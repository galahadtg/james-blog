"""User model for authentication and profile management."""

from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class User(TimestampMixin, Base):
    """Application user with authentication support.

    Passwords are stored as hashes only — never plaintext.
    Each user has a role that determines their permissions.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Foreign Keys
    role_id: Mapped[int | None] = mapped_column(
        ForeignKey("roles.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Relationships
    role = relationship("Role", back_populates="users", lazy="selectin")
    posts = relationship("Post", back_populates="author", lazy="dynamic")
    comments = relationship(
        "Comment", back_populates="author", lazy="dynamic",
        foreign_keys="Comment.author_id",
    )

    @property
    def permissions(self) -> list[str]:
        """Get all permission codenames for this user's role."""
        if self.role and self.role.permissions:
            return [p.codename for p in self.role.permissions]
        return []

    def has_permission(self, codename: str) -> bool:
        """Check if the user has a specific permission via their role."""
        return codename in self.permissions

    def __repr__(self) -> str:
        return f"<User {self.username}>"
