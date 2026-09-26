"""Tests for authorization and permission enforcement."""


class TestAuthorization:
    """Test that permission checks work correctly."""

    def test_user_permissions_limited(self, client, user_token):
        """Regular user should have exactly 4 permissions."""
        me = client.get("/api/auth/me",
            headers={"Authorization": f"Bearer {user_token}"})
        perms = me.json().get("permissions", [])
        assert len(perms) == 4

    def test_admin_has_broad_permissions(self, client, admin_token):
        """Admin should have many permissions."""
        me = client.get("/api/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"})
        perms = me.json().get("permissions", [])
        assert len(perms) >= 20

    def test_user_cannot_list_users(self, client, user_token):
        """Regular user lacks user.read."""
        resp = client.get("/api/users/",
            headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 403

    def test_admin_can_list_users(self, client, admin_token):
        """Admin has user.read."""
        resp = client.get("/api/users/",
            headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200

    def test_user_cannot_list_roles(self, client, user_token):
        """Regular user lacks role.read."""
        resp = client.get("/api/roles/",
            headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 403

    def test_admin_can_list_roles(self, client, admin_token):
        """Admin has role.read."""
        resp = client.get("/api/roles/",
            headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200

    def test_author_has_6_permissions(self, client, author_token):
        """Author should have 8 permissions (6 + 2 media)."""
        me = client.get("/api/auth/me",
            headers={"Authorization": f"Bearer {author_token}"})
        perms = me.json().get("permissions", [])
        assert len(perms) == 8

    def test_inactive_user_denied(self, client, test_user, db_session):
        """Deactivated users should be blocked."""
        test_user.is_active = False
        db_session.commit()
        resp = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "password123",
        })
        assert resp.status_code == 403
