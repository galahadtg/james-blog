"""User service - handles user business logic.

Keeps password hashing, slug generation, and search logic
out of the router layer.
"""

from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.base import BaseService


class UserService(BaseService[User]):
    """Service for User CRUD and authentication-related operations."""

    def __init__(self, db: Session):
        super().__init__(db, User)

    def get_by_email(self, email: str) -> User | None:
        """Find a user by email address."""
        stmt = select(User).where(User.email == email)
        return self.db.scalar(stmt)

    def get_by_username(self, username: str) -> User | None:
        """Find a user by username."""
        stmt = select(User).where(User.username == username)
        return self.db.scalar(stmt)

    def search(self, query: str, *, skip: int = 0, limit: int = 20) -> list[User]:
        """Search users by username or email."""
        stmt = (
            select(User)
            .where(
                or_(
                    User.username.ilike(f"%{query}%"),
                    User.email.ilike(f"%{query}%"),
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
