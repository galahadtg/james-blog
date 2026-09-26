"""Database models.

Import all models here so Alembic can discover them for auto-migrations.
"""

from app.models.user import User
from app.models.category import Category
from app.models.post import Post
from app.models.comment import Comment
from app.models.media import Media
from app.models.notification import Notification
from app.models.audit_log import AuditLog
from app.models.role import Role, Permission, role_permission

__all__ = ["User", "Category", "Post", "Comment", "Media", "Notification", "AuditLog", "Role", "Permission", "role_permission"]
