"""Comment model for post comments and moderation."""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class Comment(TimestampMixin, Base):
    """User comment on a post.

    Supports:
      - Nested replies (via parent_id)
      - Moderation workflow (approved / pending / rejected)
      - Soft-delete via is_removed flag
    """

    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False, index=True
    )
    is_removed: Mapped[bool] = mapped_column(default=False, nullable=False)
    moderated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    moderated_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Foreign Keys
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"), nullable=True, index=True
    )

    # Relationships
    author = relationship("User", back_populates="comments", foreign_keys=[author_id])
    post = relationship("Post", back_populates="comments")
    parent = relationship("Comment", back_populates="replies", remote_side="Comment.id")
    replies = relationship(
        "Comment", back_populates="parent", lazy="dynamic",
        foreign_keys=[parent_id],
    )
    moderator = relationship(
        "User", foreign_keys=[moderated_by],
    )

    def __repr__(self) -> str:
        return f"<Comment {self.id} by user {self.author_id} on post {self.post_id}>"
