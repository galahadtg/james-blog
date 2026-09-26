"""Users router - REST API for user management.

Demonstrates:
  - Service layer integration
  - Proper HTTP status codes
  - Response models that exclude sensitive data
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService
from app.core.authorization import require_permission, Perm
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Perm.USER_READ)),
):
    """Get all users with optional search and pagination."""
    service = UserService(db)
    if search:
        return service.search(search, skip=skip, limit=limit)
    return service.get_all(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Perm.USER_READ)),
):
    """Get a single user by ID."""
    service = UserService(db)
    user = service.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Perm.USER_UPDATE)),
):
    """Update a user (partial update)."""
    service = UserService(db)

    # Check for duplicate email
    if user_data.email:
        existing = service.get_by_email(user_data.email)
        if existing and existing.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

    user = service.update(
        user_id,
        username=user_data.username,
        email=user_data.email,
        is_active=user_data.is_active,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Perm.USER_DELETE)),
):
    """Deactivate a user."""
    service = UserService(db)
    user = service.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    # Soft delete: deactivate instead of removing
    service.update(user_id, is_active=False)
    return
