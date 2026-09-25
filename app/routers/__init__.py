"""API routers - HTTP endpoints for all resources."""

from app.routers.posts import router as posts_router
from app.routers.users import router as users_router
from app.routers.categories import router as categories_router

__all__ = ["posts_router", "users_router", "categories_router"]
