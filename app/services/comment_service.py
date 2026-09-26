"""Comment service with moderation and filtering."""

from datetime import datetime, timezone

from sqlalchemy import select, or_

from app.database.session import Session
from app.models.comment import Comment
from app.services.base import BaseService


class CommentService(BaseService[Comment]):
    """Service for comment management with moderation support."""

    def __init__(self, db: Session):
        super().__init__(db, Comment)

    def get_by_post(
        self, post_id: int, *, skip: int = 0, limit: int = 100, approved_only: bool = True
    ) -> list[Comment]:
        """Get comments for a specific post."""
        stmt = (
            select(Comment)
            .where(Comment.post_id == post_id)
            .where(Comment.is_removed == False)
            .offset(skip)
            .limit(limit)
            .order_by(Comment.created_at.asc())
        )
        if approved_only:
            stmt = stmt.where(Comment.status == "approved")
        return list(self.db.scalars(stmt).all())

    def get_pending(
        self, *, skip: int = 0, limit: int = 100
    ) -> list[Comment]:
        """Get all comments pending moderation."""
        stmt = (
            select(Comment)
            .where(Comment.status == "pending")
            .where(Comment.is_removed == False)
            .offset(skip)
            .limit(limit)
            .order_by(Comment.created_at.asc())
        )
        return list(self.db.scalars(stmt).all())

    def moderate(
        self, comment_id: int, status: str, moderator_id: int
    ) -> Comment | None:
        """Approve or reject a comment."""
        comment = self.get(comment_id)
        if not comment:
            return None
        comment.status = status
        comment.moderated_at = datetime.now(timezone.utc)
        comment.moderated_by = moderator_id
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def remove(self, comment_id: int) -> Comment | None:
        """Soft-delete a comment (marks as removed but keeps in DB)."""
        comment = self.get(comment_id)
        if not comment:
            return None
        comment.is_removed = True
        self.db.commit()
        self.db.refresh(comment)
        return comment
