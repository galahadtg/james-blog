"""Authorization dependencies for permission-based access control.

Usage:
    # Protect a single endpoint
    @router.get("/posts")
    async def list_posts(
        current_user: User = Depends(require_permission("post.read"))
    ): ...

    # Combine auth + permission
    @router.delete("/posts/{id}")
    async def delete_post(
        current_user: User = Depends(require_permission("post.delete"))
    ): ...

    # Super admin bypass - users with 'admin.access' or 'superadmin' role
    # have all permissions automatically.
"""

from functools import lru_cache

from fastapi import Depends, HTTPException, status

from app.core.dependencies import get_current_user
from app.models.user import User

# Permissions that grant blanket access to everything
ADMIN_OVERRIDE_PERMISSIONS = {"admin.access", "*"}


class require_permission:
    """FastAPI dependency that checks if the user has a specific permission.

    Can be used as a callable class (not a function) so we can pass
    the permission name as an argument.

    Example:
        @router.get("/admin")
        async def admin_panel(
            user: User = Depends(require_permission("admin.access"))
        ):
    """

    def __init__(self, codename: str):
        self.codename = codename

    def __call__(
        self, current_user: User = Depends(get_current_user)
    ) -> User:
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated.",
            )

        # Check if user has the specific permission or an admin override
        user_perms = current_user.permissions
        if self.codename in user_perms:
            return current_user

        # Check for admin overrides
        if any(p in user_perms for p in ADMIN_OVERRIDE_PERMISSIONS):
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Permission denied. Required: '{self.codename}'. "
                f"Your role has: {user_perms or 'none'}"
            ),
        )


# ---------------------------------------------------------------------------
# Permission constants - single source of truth
# ---------------------------------------------------------------------------
# These are used both for seeding the database and for route protection.


class Perm:
    """Namespace for all permission codenames.

    Using a class with string constants ensures we never mistype
    a permission name — autocomplete shows all options.
    """

    # Posts
    POST_CREATE = "post.create"
    POST_READ = "post.read"
    POST_UPDATE = "post.update"
    POST_DELETE = "post.delete"
    POST_PUBLISH = "post.publish"

    # Categories
    CATEGORY_CREATE = "category.create"
    CATEGORY_READ = "category.read"
    CATEGORY_UPDATE = "category.update"
    CATEGORY_DELETE = "category.delete"

    # Users
    USER_CREATE = "user.create"
    USER_READ = "user.read"
    USER_UPDATE = "user.update"
    USER_DELETE = "user.delete"

    # Roles & Permissions
    ROLE_CREATE = "role.create"
    ROLE_READ = "role.read"
    ROLE_UPDATE = "role.update"
    ROLE_DELETE = "role.delete"

    # Comments
    COMMENT_CREATE = "comment.create"
    COMMENT_READ = "comment.read"
    COMMENT_UPDATE = "comment.update"
    COMMENT_DELETE = "comment.delete"
    COMMENT_MODERATE = "comment.moderate"

    # Media
    MEDIA_CREATE = "media.create"
    MEDIA_READ = "media.read"
    MEDIA_UPDATE = "media.update"
    MEDIA_DELETE = "media.delete"

    # Admin
    ADMIN_ACCESS = "admin.access"

    # System
    SETTINGS_MANAGE = "settings.manage"


# All permissions grouped by resource for seeding
ALL_PERMISSIONS: dict[str, list[tuple[str, str, str]]] = {
    "Posts": [
        (Perm.POST_CREATE, "Create Post", "Can create new posts"),
        (Perm.POST_READ, "Read Post", "Can view posts"),
        (Perm.POST_UPDATE, "Update Post", "Can edit any post"),
        (Perm.POST_DELETE, "Delete Post", "Can delete any post"),
        (Perm.POST_PUBLISH, "Publish Post", "Can publish/unpublish posts"),
    ],
    "Categories": [
        (Perm.CATEGORY_CREATE, "Create Category", "Can create categories"),
        (Perm.CATEGORY_READ, "Read Category", "Can view categories"),
        (Perm.CATEGORY_UPDATE, "Update Category", "Can edit categories"),
        (Perm.CATEGORY_DELETE, "Delete Category", "Can delete categories"),
    ],
    "Users": [
        (Perm.USER_CREATE, "Create User", "Can create users"),
        (Perm.USER_READ, "Read User", "Can view user profiles"),
        (Perm.USER_UPDATE, "Update User", "Can edit users"),
        (Perm.USER_DELETE, "Delete User", "Can deactivate users"),
    ],
    "Roles": [
        (Perm.ROLE_CREATE, "Create Role", "Can create roles"),
        (Perm.ROLE_READ, "Read Role", "Can view roles and permissions"),
        (Perm.ROLE_UPDATE, "Update Role", "Can edit roles"),
        (Perm.ROLE_DELETE, "Delete Role", "Can delete roles"),
    ],
    "Comments": [
        (Perm.COMMENT_CREATE, "Create Comment", "Can post comments"),
        (Perm.COMMENT_READ, "Read Comment", "Can view comments"),
        (Perm.COMMENT_UPDATE, "Update Comment", "Can edit own comments"),
        (Perm.COMMENT_DELETE, "Delete Comment", "Can delete comments"),
        (Perm.COMMENT_MODERATE, "Moderate Comment", "Can approve/reject comments"),
    ],
    "Media": [
        (Perm.MEDIA_CREATE, "Upload Media", "Can upload files"),
        (Perm.MEDIA_READ, "Read Media", "Can view media files"),
        (Perm.MEDIA_UPDATE, "Update Media", "Can edit media metadata"),
        (Perm.MEDIA_DELETE, "Delete Media", "Can delete media files"),
    ],
    "Admin": [
        (Perm.ADMIN_ACCESS, "Admin Access", "Can access admin panel"),
    ],
    "System": [
        (Perm.SETTINGS_MANAGE, "Manage Settings", "Can change system settings"),
    ],
}


def get_all_permission_defs() -> list[tuple[str, str, str, str]]:
    """Flatten ALL_PERMISSIONS into a list of (group, codename, name, description)."""
    result = []
    for group, perms in ALL_PERMISSIONS.items():
        for codename, name, description in perms:
            result.append((group, codename, name, description))
    return result
