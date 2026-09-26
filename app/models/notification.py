"""Notification model for user alerts and activity updates."""

from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class Notification(TimestampMixin, Base):
    """User notification for system events.

    Created automatically when events occur (comments, replies, etc.).
    """

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True, default="info"
    )
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    link: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Foreign Keys
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Relationships
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<Notification {self.type} for user {self.user_id}: {self.message[:50]}>"
