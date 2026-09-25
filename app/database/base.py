"""SQLAlchemy declarative base and common mixins.

All database models inherit from `Base` which gives them:
  - Table name auto-generation from class name
  - Metadata for Alembic migrations
  - Common columns via mixins

The `TimestampMixin` adds `created_at` and `updated_at` columns
to any model that includes it.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models.

    Using SQLAlchemy 2.0 `DeclarativeBase` (modern style).
    Older tutorials use `declarative_base()` function - this is
    the newer, preferred approach.
    """
    pass


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamp columns.

    Usage:
        class User(TimestampMixin, Base):
            __tablename__ = "users"
            ...

    Both timestamps are timezone-aware (UTC).
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
