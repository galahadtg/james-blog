"""Pydantic schemas for authentication.

Separate schemas for:
  - Registration (what the user sends to sign up)
  - Login (credentials)
  - Token response (what the API returns)
  - Current user info (from JWT)
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Schema for user registration."""

    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """Schema returned on successful authentication."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Schema for refreshing an expired access token."""

    refresh_token: str


class CurrentUserResponse(BaseModel):
    """Schema for the current authenticated user."""

    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    permissions: list[str] = []

    model_config = {"from_attributes": True}
