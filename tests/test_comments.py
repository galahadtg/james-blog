"""Tests for comment CRUD, moderation, and permissions."""


class TestComments:
    """Test comment creation, listing, moderation, and deletion."""

    def _create_post(self, client, token):
        """Helper to create a test post."""
        resp = client.post("/api/posts/", json={
            "title": "Commentable Post",
            "content": "Post for comments",
        }, headers={"Authorization": f"Bearer {token}"})
        return resp.json()["id"]

    def test_create_comment(self, client, admin_token):
        """Create a comment on a post."""
        post_id = self._create_post(client, admin_token)
        resp = client.post("/api/comments/", json={
            "content": "Great post!",
            "post_id": post_id,
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 201
        assert resp.json()["content"] == "Great post!"
        assert resp.json()["status"] == "approved"

    def test_create_comment_requires_auth(self, client):
        """Creating a comment without auth returns 401."""
        resp = client.post("/api/comments/", json={
            "content": "No auth",
            "post_id": 1,
        })
        assert resp.status_code == 401

    def test_list_comments_public(self, client, admin_token):
        """Anyone can list approved comments."""
        post_id = self._create_post(client, admin_token)
        client.post("/api/comments/", json={
            "content": "Public comment",
            "post_id": post_id,
        }, headers={"Authorization": f"Bearer {admin_token}"})
        resp = client.get(f"/api/comments/?post_id={post_id}")
        assert resp.status_code == 200
        assert len(resp.json()) > 0

    def test_moderate_comment(self, client, admin_token):
        """Admin can moderate comments."""
        post_id = self._create_post(client, admin_token)
        create = client.post("/api/comments/", json={
            "content": "Needs moderation",
            "post_id": post_id,
        }, headers={"Authorization": f"Bearer {admin_token}"})
        comment_id = create.json()["id"]
        resp = client.post(f"/api/comments/{comment_id}/moderate", json={
            "status": "rejected",
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "rejected"

    def test_user_cannot_moderate(self, client, user_token, admin_token):
        """Regular user lacks comment.moderate."""
        post_id = self._create_post(client, admin_token)
        create = client.post("/api/comments/", json={
            "content": "Test comment",
            "post_id": post_id,
        }, headers={"Authorization": f"Bearer {admin_token}"})
        resp = client.post(f"/api/comments/{create.json()['id']}/moderate", json={
            "status": "rejected",
        }, headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 403

    def test_delete_comment(self, client, admin_token):
        """Admin can soft-delete comments."""
        post_id = self._create_post(client, admin_token)
        create = client.post("/api/comments/", json={
            "content": "Will be deleted",
            "post_id": post_id,
        }, headers={"Authorization": f"Bearer {admin_token}"})
        comment_id = create.json()["id"]
        resp = client.delete(f"/api/comments/{comment_id}",
            headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 204
