"""Audit log model for tracking important system actions."""

from datetime import datetime

from sqlalchemy import String, Text, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class AuditLog(Base):
    """Immutable audit trail for tracking important actions.

    Logs are write-only — once created they cannot be modified or deleted
    through the API (enforced at the service level).
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    actor_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, index=True, comment="User who performed the action"
    )
    action: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True, comment="Action type (create, update, delete, login, etc.)"
    )
    resource: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True, comment="Resource type (post, user, comment, etc.)"
    )
    resource_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="ID of the affected resource"
    )
    detail: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="JSON or human-readable details"
    )
    ip_address: Mapped[str | None] = mapped_column(
        String(45), nullable=True, comment="Client IP address"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} on {self.resource} by user {self.actor_id}>"
