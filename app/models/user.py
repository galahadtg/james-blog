"""User model for authentication and profile management."""

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class User(TimestampMixin, Base):
    """Application user with authentication support.

    Passwords are stored as hashes only — never plaintext.
    The 'posts' relationship lets us navigate from a user to
    all posts they've authored.
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

    # Relationships
    posts = relationship("Post", back_populates="author", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<User {self.username}>"
