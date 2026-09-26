"""Tests for category CRUD endpoints."""


class TestCategories:
    """Test category creation, listing, updating, and deletion."""

    def test_list_categories_public(self, client):
        """Anyone can list categories."""
        resp = client.get("/api/categories/")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_create_category_requires_auth(self, client):
        """Creating a category without auth returns 401."""
        resp = client.post("/api/categories/", json={
            "name": "Tech",
        })
        assert resp.status_code == 401

    def test_user_cannot_create_category(self, client, user_token):
        """Regular user lacks category.create."""
        resp = client.post("/api/categories/", json={
            "name": "Tech",
        }, headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 403

    def test_admin_can_create_category(self, client, admin_token):
        """Admin can create categories."""
        resp = client.post("/api/categories/", json={
            "name": "Technology",
            "description": "Tech-related posts",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Technology"
        assert data["slug"] == "technology"

    def test_admin_can_update_category(self, client, admin_token):
        """Admin can update categories."""
        create = client.post("/api/categories/", json={
            "name": "Original",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        cat_id = create.json()["id"]
        resp = client.patch(f"/api/categories/{cat_id}", json={
            "name": "Updated Name",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Name"

    def test_admin_can_delete_category(self, client, admin_token):
        """Admin can delete categories."""
        create = client.post("/api/categories/", json={
            "name": "Temp Category",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        cat_id = create.json()["id"]
        resp = client.delete(f"/api/categories/{cat_id}",
            headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 204

    def test_author_cannot_delete_category(self, client, author_token):
        """Author lacks category.delete."""
        resp = client.delete("/api/categories/1",
            headers={"Authorization": f"Bearer {author_token}"})
        assert resp.status_code == 403
