"""Pydantic schemas for Notification requests and responses."""

from datetime import datetime
from pydantic import BaseModel, Field


class NotificationResponse(BaseModel):
    """Schema for returning a notification in API responses."""

    id: int
    type: str
    message: str
    link: str | None
    is_read: bool
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UnreadCountResponse(BaseModel):
    """Schema for unread notification count."""

    count: int
