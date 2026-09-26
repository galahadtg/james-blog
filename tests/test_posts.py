"""Tests for post CRUD endpoints and authorization."""


class TestPosts:
    """Test post creation, listing, updating, and deletion."""

    def test_list_posts_public(self, client):
        """Anyone can list posts (no auth required)."""
        resp = client.get("/api/posts/")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_post_not_found(self, client):
        """Getting a non-existent post returns 404."""
        resp = client.get("/api/posts/99999")
        assert resp.status_code == 404

    def test_create_post_requires_auth(self, client):
        """Creating a post without auth returns 401."""
        resp = client.post("/api/posts/", json={
            "title": "My Post",
            "content": "Post content",
        })
        assert resp.status_code == 401

    def test_user_cannot_create_post(self, client, user_token):
        """Regular user lacks post.create permission."""
        resp = client.post("/api/posts/", json={
            "title": "My Post",
            "content": "Post content",
        }, headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 403

    def test_author_can_create_post(self, client, author_token):
        """Author can create posts."""
        resp = client.post("/api/posts/", json={
            "title": "Author Post",
            "content": "Written by an author",
            "published": False,
        }, headers={"Authorization": f"Bearer {author_token}"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Author Post"
        assert data["status"] == "draft"
        assert data["slug"] == "author-post"
        assert "id" in data

    def test_author_can_update_post(self, client, author_token):
        """Author can update their own posts."""
        # Create
        create = client.post("/api/posts/", json={
            "title": "Post to Update",
            "content": "Original content",
        }, headers={"Authorization": f"Bearer {author_token}"})
        post_id = create.json()["id"]
        # Update
        resp = client.put(f"/api/posts/{post_id}", json={
            "content": "Updated content",
        }, headers={"Authorization": f"Bearer {author_token}"})
        assert resp.status_code == 200
        assert resp.json()["content"] == "Updated content"

    def test_author_cannot_publish(self, client, author_token):
        """Author lacks post.publish permission."""
        create = client.post("/api/posts/", json={
            "title": "Draft Post",
            "content": "Cannot publish",
        }, headers={"Authorization": f"Bearer {author_token}"})
        post_id = create.json()["id"]
        resp = client.post(f"/api/posts/{post_id}/publish",
            headers={"Authorization": f"Bearer {author_token}"})
        assert resp.status_code == 403

    def test_admin_can_publish(self, client, admin_token):
        """Admin can publish posts."""
        create = client.post("/api/posts/", json={
            "title": "Admin Post",
            "content": "Publishing now",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        post_id = create.json()["id"]
        resp = client.post(f"/api/posts/{post_id}/publish",
            headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "published"
        assert resp.json()["published_at"] is not None

    def test_admin_can_unpublish(self, client, admin_token):
        """Admin can unpublish posts."""
        create = client.post("/api/posts/", json={
            "title": "Publish Then Unpublish",
            "content": "Testing",
            "published": True,
        }, headers={"Authorization": f"Bearer {admin_token}"})
        post_id = create.json()["id"]
        resp = client.post(f"/api/posts/{post_id}/unpublish",
            headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "draft"

    def test_admin_can_delete_post(self, client, admin_token):
        """Admin can delete posts."""
        create = client.post("/api/posts/", json={
            "title": "Post to Delete",
            "content": "Will be deleted",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        post_id = create.json()["id"]
        resp = client.delete(f"/api/posts/{post_id}",
            headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 204

    def test_user_cannot_delete_post(self, client, user_token, admin_token):
        """Regular user lacks post.delete permission."""
        create = client.post("/api/posts/", json={
            "title": "Admin Post",
            "content": "Content",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        post_id = create.json()["id"]
        resp = client.delete(f"/api/posts/{post_id}",
            headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 403
