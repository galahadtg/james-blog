"""Notification service for creating and managing user notifications."""

from sqlalchemy import select, func

from app.models.notification import Notification
from app.services.base import BaseService


class NotificationService(BaseService[Notification]):
    """Service for user notification management."""

    def __init__(self, db):
        super().__init__(db, Notification)

    def create_notification(
        self, user_id: int, type: str, message: str, link: str | None = None
    ) -> Notification:
        """Create a new notification for a user."""
        return self.create(
            user_id=user_id,
            type=type,
            message=message,
            link=link,
        )

    def get_user_notifications(
        self, user_id: int, *, skip: int = 0, limit: int = 50, unread_only: bool = False
    ) -> list[Notification]:
        """Get notifications for a specific user, newest first."""
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        if unread_only:
            stmt = stmt.where(Notification.is_read == False)
        return list(self.db.scalars(stmt).all())

    def mark_as_read(self, notification_id: int, user_id: int) -> Notification | None:
        """Mark a single notification as read."""
        notification = self.get(notification_id)
        if not notification or notification.user_id != user_id:
            return None
        notification.is_read = True
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all unread notifications as read. Returns count updated."""
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .where(Notification.is_read == False)
        )
        unread = list(self.db.scalars(stmt).all())
        count = len(unread)
        for n in unread:
            n.is_read = True
        self.db.commit()
        return count

    def get_unread_count(self, user_id: int) -> int:
        """Get the number of unread notifications for a user."""
        stmt = (
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id)
            .where(Notification.is_read == False)
        )
        return self.db.scalar(stmt) or 0
