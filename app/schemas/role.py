"""Pydantic schemas for roles and permissions."""

from datetime import datetime
from pydantic import BaseModel, Field


class PermissionResponse(BaseModel):
    """Schema for returning permission data."""

    id: int
    codename: str
    name: str
    description: str | None

    model_config = {"from_attributes": True}


class RoleCreate(BaseModel):
    """Schema for creating a new role."""

    name: str = Field(..., min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=500)
    permission_ids: list[int] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    """Schema for updating a role."""

    name: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = None
    permission_ids: list[int] | None = None


class RoleResponse(BaseModel):
    """Schema for returning role data with permissions."""

    id: int
    name: str
    description: str | None
    is_system_role: bool
    created_at: datetime
    updated_at: datetime
    permissions: list[PermissionResponse] = []

    model_config = {"from_attributes": True}
