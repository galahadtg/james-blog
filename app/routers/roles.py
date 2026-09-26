"""Roles router - admin endpoints for managing roles and permissions."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.authorization import require_permission, Perm
from app.models.user import User
from app.schemas.role import RoleCreate, RoleResponse, RoleUpdate, PermissionResponse
from app.services.role_service import RoleService, PermissionService

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("/", response_model=list[RoleResponse])
async def get_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Perm.ROLE_READ)),
):
    """List all roles with their permissions."""
    service = RoleService(db)
    return service.get_all()


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Perm.ROLE_READ)),
):
    """Get a single role with its permissions."""
    service = RoleService(db)
    role = service.get(role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return role


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Perm.ROLE_CREATE)),
):
    """Create a new role with optional permissions."""
    service = RoleService(db)
    if service.get_by_name(data.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role name already exists",
        )
    role = service.create(name=data.name, description=data.description)
    if data.permission_ids:
        role = service.set_permissions(role.id, data.permission_ids)
    return role


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Perm.ROLE_UPDATE)),
):
    """Update a role's name, description, and permissions."""
    service = RoleService(db)
    role = service.get(role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    if role.is_system_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System roles cannot be modified",
        )
    if data.name is not None:
        role = service.update(role_id, name=data.name, description=data.description)
    if data.permission_ids is not None:
        role = service.set_permissions(role_id, data.permission_ids)
    return role


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Perm.ROLE_DELETE)),
):
    """Delete a role."""
    service = RoleService(db)
    role = service.get(role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    if role.is_system_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System roles cannot be deleted",
        )
    service.delete(role_id)


@router.get("/permissions/all", response_model=list[PermissionResponse])
async def list_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Perm.ROLE_READ)),
):
    """List all available permissions."""
    service = PermissionService(db)
    return service.get_all()
