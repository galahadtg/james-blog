"""Pydantic schemas for Audit Log responses."""

from datetime import datetime
from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    """Schema for returning an audit log entry."""

    id: int
    actor_id: int | None
    action: str
    resource: str
    resource_id: int | None
    detail: str | None
    ip_address: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
