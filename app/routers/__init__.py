"""API routers - HTTP endpoints for all resources."""

from app.routers.posts import router as posts_router
from app.routers.users import router as users_router
from app.routers.categories import router as categories_router
from app.routers.comments import router as comments_router
from app.routers.media import router as media_router
from app.routers.notifications import router as notifications_router
from app.routers.audit_logs import router as audit_logs_router

__all__ = ["posts_router", "users_router", "categories_router", "comments_router", "media_router", "notifications_router", "audit_logs_router"]
