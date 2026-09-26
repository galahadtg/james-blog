"""Tests for authentication endpoints."""

import pytest


class TestAuth:
    """Test registration, login, token refresh, and user profile."""

    def test_register(self, client):
        """Register a new user successfully."""
        resp = client.post("/api/auth/register", json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "securepass123",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
        assert "password" not in data
        assert data["is_active"] is True

    def test_register_duplicate_username(self, client, test_user):
        """Register with an existing username should fail."""
        resp = client.post("/api/auth/register", json={
            "username": "testuser",
            "email": "other@example.com",
            "password": "securepass123",
        })
        assert resp.status_code == 409
        assert "already" in resp.json()["detail"].lower()

    def test_register_duplicate_email(self, client, test_user):
        """Register with an existing email should fail."""
        resp = client.post("/api/auth/register", json={
            "username": "otheruser",
            "email": "test@example.com",
            "password": "securepass123",
        })
        assert resp.status_code == 409
        assert "already" in resp.json()["detail"].lower()

    def test_login_success(self, client, test_user):
        """Login with valid credentials returns tokens."""
        resp = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "password123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        """Login with wrong password returns 401."""
        resp = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "wrongpassword",
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Login with unregistered email returns 401."""
        resp = client.post("/api/auth/login", json={
            "email": "nobody@example.com",
            "password": "password123",
        })
        assert resp.status_code == 401

    def test_me_authenticated(self, client, user_token):
        """Get current user with valid token."""
        resp = client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {user_token}",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "password" not in data

    def test_me_unauthenticated(self, client):
        """Get current user without token returns 401."""
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_token_refresh(self, client, test_user):
        """Refresh token returns new tokens."""
        login = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "password123",
        })
        refresh_token = login.json()["refresh_token"]
        resp = client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_token_refresh_invalid(self, client):
        """Refresh with invalid token returns 401."""
        resp = client.post("/api/auth/refresh", json={
            "refresh_token": "invalid-token-here",
        })
        assert resp.status_code == 401


class TestAuthPermissions:
    """Test that users get default role on registration."""

    def test_default_role_assigned(self, client, seed_roles):
        """New user should get the default 'user' role."""
        resp = client.post("/api/auth/register", json={
            "username": "defaultroleuser",
            "email": "default@example.com",
            "password": "password123",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "permissions" in data
        assert len(data["permissions"]) == 4  # user role has 4 permissions
