"""Audit log service for recording and querying system actions.

Audit logs are append-only: entries can be created and read but
never modified or deleted through the service layer.
"""

from typing import Any

from sqlalchemy import select

from app.models.audit_log import AuditLog
from app.services.base import BaseService


class AuditLogService(BaseService[AuditLog]):
    """Service for audit trail management (append-only)."""

    def __init__(self, db):
        super().__init__(db, AuditLog)

    def log(
        self,
        actor_id: int | None,
        action: str,
        resource: str,
        resource_id: int | None = None,
        detail: str | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        """Record an immutable audit log entry."""
        entry = AuditLog(
            actor_id=actor_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            detail=detail,
            ip_address=ip_address,
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def get_by_resource(
        self, resource: str, resource_id: int, *, skip: int = 0, limit: int = 50
    ) -> list[AuditLog]:
        """Get audit logs for a specific resource."""
        stmt = (
            select(AuditLog)
            .where(AuditLog.resource == resource)
            .where(AuditLog.resource_id == resource_id)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_by_actor(
        self, actor_id: int, *, skip: int = 0, limit: int = 50
    ) -> list[AuditLog]:
        """Get audit logs for a specific user."""
        stmt = (
            select(AuditLog)
            .where(AuditLog.actor_id == actor_id)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    # Override to prevent modification/deletion
    def update(self, id: int, **kwargs: Any) -> None:
        """Not allowed — audit logs are immutable."""
        raise NotImplementedError("Audit logs are append-only and cannot be updated.")

    def delete(self, id: int) -> bool:
        """Not allowed — audit logs are immutable."""
        raise NotImplementedError("Audit logs are append-only and cannot be deleted.")
