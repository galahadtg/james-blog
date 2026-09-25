"""Category service - handles category business logic.

Generates URL-friendly slugs from category names
and provides search functionality.
"""

import re
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.services.base import BaseService


class CategoryService(BaseService[Category]):
    """Service for Category CRUD operations."""

    def __init__(self, db: Session):
        super().__init__(db, Category)

    @staticmethod
    def _slugify(name: str) -> str:
        """Convert a name into a URL-friendly slug.

        Example: "Technology News" -> "technology-news"
        """
        slug = name.lower().strip()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug.strip("-")

    def get_by_slug(self, slug: str) -> Category | None:
        """Find a category by its slug."""
        stmt = select(Category).where(Category.slug == slug)
        return self.db.scalar(stmt)

    def create(self, **kwargs) -> Category:
        """Create a category, auto-generating slug from name if not provided."""
        if "slug" not in kwargs or not kwargs["slug"]:
            kwargs["slug"] = self._slugify(kwargs.get("name", ""))
        return super().create(**kwargs)

    def update(self, id: int, **kwargs) -> Category | None:
        """Update a category, regenerating slug if name changed."""
        if kwargs.get("name") and "slug" not in kwargs:
            kwargs["slug"] = self._slugify(kwargs["name"])
        return super().update(id, **kwargs)
