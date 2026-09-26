"""Categories router - REST API for category management."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services.category_service import CategoryService
from app.core.authorization import require_permission, Perm
from app.models.user import User

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=list[CategoryResponse])
async def get_categories(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Get all categories with pagination (public)."""
    service = CategoryService(db)
    return service.get_all(skip=skip, limit=limit)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a single category by ID (public)."""
    service = CategoryService(db)
    category = service.get(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found",
        )
    return category


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Perm.CATEGORY_CREATE)),
):
    """Create a new category."""
    service = CategoryService(db)
    return service.create(
        name=category_data.name,
        description=category_data.description,
    )


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Perm.CATEGORY_UPDATE)),
):
    """Update a category."""
    service = CategoryService(db)
    category = service.update(
        category_id,
        name=category_data.name,
        description=category_data.description,
    )
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found",
        )
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Perm.CATEGORY_DELETE)),
):
    """Delete a category."""
    service = CategoryService(db)
    deleted = service.delete(category_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found",
        )
    return
