"""Pydantic schemas for User requests and responses.

Note: password_hash is NEVER included in response schemas.
The response schema uses `model_config` to exclude it by default.
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseModel):
    """Schema for updating an existing user (all fields optional)."""

    username: str | None = Field(default=None, min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    """Schema for returning user data in API responses.

    Note: password_hash is deliberately excluded.
    """

    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
