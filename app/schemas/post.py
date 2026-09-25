"""Pydantic schemas for Post requests and responses.

Separates request schemas (what the client sends) from
response schemas (what the API returns). This ensures we
never accidentally expose internal data.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class PostCreate(BaseModel):
    """Schema for creating a new post."""

    title: str = Field(..., min_length=1, max_length=200, description="Post title")
    content: str = Field(..., min_length=1, description="Post body content")
    excerpt: str | None = Field(default=None, max_length=500)
    published: bool = Field(default=False, description="Publish immediately")
    category_id: int | None = Field(default=None, description="Category ID")


class PostUpdate(BaseModel):
    """Schema for updating an existing post (all fields optional for PATCH)."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1)
    excerpt: str | None = Field(default=None, max_length=500)
    category_id: int | None = None


class PostResponse(BaseModel):
    """Schema for returning a post in API responses.

    Maps the database model fields to the API response.
    `published` is derived from `status` for convenience.
    """

    id: int
    title: str
    slug: str
    content: str
    excerpt: str | None
    status: str
    published_at: datetime | None
    author_id: int
    category_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
