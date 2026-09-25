"""Post service - handles post business logic.

Manages slug generation, status transitions, filtering,
and search — keeping the router focused on HTTP concerns.
"""

import re
from datetime import datetime, timezone

from sqlalchemy import select, or_, desc
from sqlalchemy.orm import Session

from app.models.post import Post
from app.services.base import BaseService


class PostService(BaseService[Post]):
    """Service for Post CRUD and content management."""

    VALID_STATUSES = {"draft", "published"}

    def __init__(self, db: Session):
        super().__init__(db, Post)

    @staticmethod
    def _slugify(title: str) -> str:
        """Convert a title into a URL-friendly slug."""
        slug = title.lower().strip()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug.strip("-")

    def get_by_slug(self, slug: str) -> Post | None:
        """Find a post by its slug."""
        stmt = select(Post).where(Post.slug == slug)
        return self.db.scalar(stmt)

    def create(self, **kwargs) -> Post:
        """Create a post, auto-generating slug from title.

        If `published=True` is passed, the post is created
        with status='published' and a published_at timestamp.
        The `published` kwarg is consumed and not passed to the model.
        """
        if "slug" not in kwargs or not kwargs["slug"]:
            kwargs["slug"] = self._slugify(kwargs.get("title", ""))

        # Handle published boolean -> status mapping
        published = kwargs.pop("published", False)
        if published:
            kwargs["status"] = "published"
            kwargs["published_at"] = datetime.now(timezone.utc)

        return super().create(**kwargs)

    def get_published(
        self, *, skip: int = 0, limit: int = 20
    ) -> list[Post]:
        """Get only published posts, newest first."""
        stmt = (
            select(Post)
            .where(Post.status == "published")
            .order_by(desc(Post.published_at))
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_by_author(self, author_id: int) -> list[Post]:
        """Get all posts by a specific author."""
        stmt = select(Post).where(Post.author_id == author_id).order_by(desc(Post.created_at))
        return list(self.db.scalars(stmt).all())

    def get_by_category(self, category_id: int) -> list[Post]:
        """Get all posts in a specific category."""
        stmt = select(Post).where(Post.category_id == category_id).order_by(desc(Post.created_at))
        return list(self.db.scalars(stmt).all())

    def search(
        self, query: str, *, skip: int = 0, limit: int = 20
    ) -> list[Post]:
        """Search posts by title or content."""
        stmt = (
            select(Post)
            .where(
                or_(
                    Post.title.ilike(f"%{query}%"),
                    Post.content.ilike(f"%{query}%"),
                )
            )
            .order_by(desc(Post.created_at))
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def publish(self, id: int) -> Post | None:
        """Set a post's status to 'published' with a timestamp."""
        post = self.get(id)
        if not post:
            return None
        post.status = "published"
        post.published_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(post)
        return post

    def unpublish(self, id: int) -> Post | None:
        """Set a post's status back to 'draft'."""
        post = self.get(id)
        if not post:
            return None
        post.status = "draft"
        post.published_at = None
        self.db.commit()
        self.db.refresh(post)
        return post
