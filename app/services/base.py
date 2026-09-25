"""Base CRUD service with common database operations.

Provides generic Create, Read, Update, Delete methods that
specific services inherit. This avoids repeating the same
patterns for every model.

Type hints ensure we get proper IDE support for each service.
"""

from typing import Any, Generic, TypeVar

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.database.base import Base

# Type variable bound to our SQLAlchemy Base
ModelType = TypeVar("ModelType", bound=Base)


class BaseService(Generic[ModelType]):
    """Generic service with common CRUD operations.

    Usage:
        class PostService(BaseService[Post]):
            def __init__(self, db: Session):
                super().__init__(db, Post)
    """

    def __init__(self, db: Session, model: type[ModelType]):
        self.db = db
        self.model = model

    def get(self, id: int) -> ModelType | None:
        """Get a single record by primary key."""
        return self.db.get(self.model, id)

    def get_all(
        self, *, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        """Get paginated records."""
        stmt = select(self.model).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def count(self) -> int:
        """Get total number of records."""
        stmt = select(func.count()).select_from(self.model)
        return self.db.scalar(stmt) or 0

    def create(self, **kwargs: Any) -> ModelType:
        """Create a new record."""
        obj = self.model(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, id: int, **kwargs: Any) -> ModelType | None:
        """Update a record by primary key. Only provided fields are changed."""
        obj = self.get(id)
        if not obj:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, id: int) -> bool:
        """Delete a record by primary key. Returns True if deleted."""
        obj = self.get(id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True
