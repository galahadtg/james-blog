"""Role service - manages roles and permissions."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.role import Role, Permission
from app.services.base import BaseService


class RoleService(BaseService[Role]):
    """Service for Role CRUD and permission management."""

    def __init__(self, db: Session):
        super().__init__(db, Role)

    def get_by_name(self, name: str) -> Role | None:
        """Find a role by name."""
        stmt = select(Role).where(Role.name == name)
        return self.db.scalar(stmt)

    def set_permissions(self, role_id: int, permission_ids: list[int]) -> Role | None:
        """Replace all permissions on a role."""
        role = self.get(role_id)
        if not role:
            return None
        stmt = select(Permission).where(Permission.id.in_(permission_ids))
        permissions = list(self.db.scalars(stmt).all())
        role.permissions = permissions
        self.db.commit()
        self.db.refresh(role)
        return role


class PermissionService(BaseService[Permission]):
    """Service for Permission CRUD."""

    def __init__(self, db: Session):
        super().__init__(db, Permission)

    def get_by_codename(self, codename: str) -> Permission | None:
        """Find a permission by codename."""
        stmt = select(Permission).where(Permission.codename == codename)
        return self.db.scalar(stmt)
