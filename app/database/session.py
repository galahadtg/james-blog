"""Database connection and session management.

Uses SQLAlchemy 2.x `create_engine` and `sessionmaker`.
The engine is created once and reused. Sessions are created per-request
using the `get_db` dependency.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import get_settings

settings = get_settings()

# Create the database engine
# The engine is the starting point for any SQLAlchemy application.
# It reads the DATABASE_URL from our settings (which comes from .env).
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,      # Verify connections before using them
    pool_size=5,             # Keep 5 connections in the pool
    max_overflow=10,         # Allow up to 10 extra connections during spikes
    echo=settings.DEBUG,     # Log SQL queries in development
)

# Session factory - creates new database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency that provides a database session.

    Usage in route handlers:
        @router.get("/")
        async def get_items(db: Session = Depends(get_db)):
            ...

    The session is automatically closed when the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
