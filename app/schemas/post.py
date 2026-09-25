"""Pydantic schemas for Post requests and responses.

Separates request schemas (what the client sends) from
response schemas (what the API returns). This ensures we
never accidentally expose internal data.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class PostBase(BaseModel):
    """Shared fields for creating and reading posts."""

    title: str = Field(..., min_length=1, max_length=200, description="Post title")
    content: str = Field(..., min_length=1, description="Post body content")
    published: bool = Field(default=False, description="Whether the post is published")


class PostCreate(PostBase):
    """Schema for creating a new post.

    Inherits all fields from PostBase.
    The 'id', 'created_at', and 'updated_at' are set by the server.
    """
    pass


class PostUpdate(BaseModel):
    """Schema for updating an existing post.

    All fields are optional so clients can send partial updates (PATCH).
    """

    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1)
    published: bool | None = Field(default=None)


class PostResponse(PostBase):
    """Schema for returning a post in API responses.

    Includes server-generated fields like 'id' and timestamps.
    """

    id: int
    created_at: datetime
    updated_at: datetime

    # This tells Pydantic to allow ORM-mode conversion
    # (we'll use this later with SQLAlchemy models)
    model_config = {"from_attributes": True}
