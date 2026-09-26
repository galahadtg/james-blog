"""Test configuration and fixtures for FastAPI Platform tests.

Uses SQLite in-memory for fast, isolated tests.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

# Set test env before importing app modules
import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["ENVIRONMENT"] = "testing"
os.environ["DEBUG"] = "False"

from app.database.base import Base
from app.database.session import get_db
from app.main import app


@pytest.fixture(scope="session")
def engine():
    """Create a SQLite engine for testing."""
    e = create_engine(
        "sqlite:///./test.db",
        connect_args={"check_same_thread": False},
    )

    # Enable WAL mode and foreign keys for SQLite
    @event.listens_for(e, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=e)
    yield e
    Base.metadata.drop_all(bind=e)


@pytest.fixture
def db_session(engine):
    """Create a fresh database session for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """FastAPI test client with overridden DB dependency."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---- Seed helpers ---- #

@pytest.fixture
def seed_permissions(db_session):
    """Seed all permissions into the test database."""
    from app.core.authorization import get_all_permission_defs
    from app.models.role import Permission

    perms = {}
    for group, codename, name, description in get_all_permission_defs():
        p = Permission(codename=codename, name=name, description=description)
        db_session.add(p)
        db_session.flush()
        perms[codename] = p
    db_session.commit()
    return perms


@pytest.fixture
def seed_roles(db_session, seed_permissions):
    """Seed default roles for testing."""
    from app.models.role import Role

    roles_data = {
        "super_admin": None,  # all perms
        "admin": [
            "post.create", "post.read", "post.update", "post.delete", "post.publish",
            "category.create", "category.read", "category.update", "category.delete",
            "user.create", "user.read", "user.update", "user.delete",
            "role.read",
            "comment.create", "comment.read", "comment.update", "comment.delete", "comment.moderate",
            "media.create", "media.read", "media.update", "media.delete",
            "admin.access",
        ],
        "editor": [
            "post.create", "post.read", "post.update", "post.delete", "post.publish",
            "category.create", "category.read", "category.update", "category.delete",
            "comment.read", "comment.update", "comment.moderate",
            "media.create", "media.read",
            "admin.access",
        ],
        "author": [
            "post.create", "post.read", "post.update",
            "category.read",
            "comment.create", "comment.read",
            "media.create", "media.read",
        ],
        "user": [
            "post.read",
            "category.read",
            "comment.create", "comment.read",
        ],
    }

    roles = {}
    for name, perm_codenames in roles_data.items():
        role = Role(name=name, description=name, is_system_role=True)
        db_session.add(role)
        db_session.flush()
        if perm_codenames is None:
            role.permissions = list(seed_permissions.values())
        else:
            role.permissions = [seed_permissions[c] for c in perm_codenames if c in seed_permissions]
        db_session.flush()
        roles[name] = role
    db_session.commit()
    return roles


@pytest.fixture
def test_user(db_session, seed_roles):
    """Create a regular user for testing."""
    from app.core.security import hash_password
    from app.models.user import User

    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("password123"),
        is_active=True,
        role_id=seed_roles["user"].id,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session, seed_roles):
    """Create an admin user for testing."""
    from app.core.security import hash_password
    from app.models.user import User

    user = User(
        username="adminuser",
        email="admin@example.com",
        password_hash=hash_password("admin123"),
        is_active=True,
        role_id=seed_roles["admin"].id,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def author_user(db_session, seed_roles):
    """Create an author user for testing."""
    from app.core.security import hash_password
    from app.models.user import User

    user = User(
        username="authoruser",
        email="author@example.com",
        password_hash=hash_password("author123"),
        is_active=True,
        role_id=seed_roles["author"].id,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_token(client, test_user):
    """Get an access token for the test user."""
    resp = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "password123",
    })
    return resp.json()["access_token"]


@pytest.fixture
def admin_token(client, admin_user):
    """Get an access token for the admin user."""
    resp = client.post("/api/auth/login", json={
        "email": "admin@example.com",
        "password": "admin123",
    })
    return resp.json()["access_token"]


@pytest.fixture
def author_token(client, author_user):
    """Get an access token for the author user."""
    resp = client.post("/api/auth/login", json={
        "email": "author@example.com",
        "password": "author123",
    })
    return resp.json()["access_token"]
