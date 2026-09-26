"""Pydantic schemas for Comment requests and responses."""

from datetime import datetime
from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    """Schema for creating a new comment."""

    content: str = Field(..., min_length=1, max_length=5000, description="Comment body")
    post_id: int = Field(..., description="ID of the post being commented on")
    parent_id: int | None = Field(default=None, description="Parent comment ID for replies")


class CommentUpdate(BaseModel):
    """Schema for editing a comment."""

    content: str | None = Field(default=None, min_length=1, max_length=5000)


class CommentModerate(BaseModel):
    """Schema for moderating a comment's status."""

    status: str = Field(
        ..., pattern="^(approved|rejected)$",
        description="New moderation status",
    )


class CommentResponse(BaseModel):
    """Schema for returning a comment in API responses."""

    id: int
    content: str
    status: str
    is_removed: bool
    moderated_at: datetime | None
    moderated_by: int | None
    author_id: int
    post_id: int
    parent_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
