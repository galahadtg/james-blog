"""Audit logs router - REST API for querying the audit trail."""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.audit_log import AuditLogResponse
from app.services.audit_log_service import AuditLogService
from app.core.authorization import require_permission, Perm
from app.models.user import User

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("/", response_model=list[AuditLogResponse])
async def list_audit_logs(
    actor_id: int | None = Query(None, description="Filter by actor"),
    resource: str | None = Query(None, description="Filter by resource type"),
    resource_id: int | None = Query(None, description="Filter by resource ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Perm.SETTINGS_MANAGE)),
):
    """List audit logs with optional filters. Requires settings.manage permission."""
    service = AuditLogService(db)

    if resource and resource_id is not None:
        return service.get_by_resource(resource, resource_id, skip=skip, limit=limit)
    if actor_id:
        return service.get_by_actor(actor_id, skip=skip, limit=limit)

    return service.get_all(skip=skip, limit=limit)


@router.get("/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Perm.SETTINGS_MANAGE)),
):
    """Get a single audit log entry."""
    service = AuditLogService(db)
    entry = service.get(log_id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit log with id {log_id} not found",
        )
    return entry
