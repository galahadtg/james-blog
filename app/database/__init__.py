"""Database package.

Provides:
  - Base: Declarative base for all models
  - engine: SQLAlchemy engine (singleton)
  - SessionLocal: Session factory
  - get_db: FastAPI dependency for request-scoped sessions
"""

from app.database.base import Base, TimestampMixin
from app.database.session import engine, SessionLocal, get_db

__all__ = ["Base", "TimestampMixin", "engine", "SessionLocal", "get_db"]
