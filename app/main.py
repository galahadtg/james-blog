"""FastAPI Platform - Main Application Entry Point.

A modular FastAPI application for Business Content & User Management.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings
from app.core.logging_config import setup_logging
from app.routers import (
    posts, users, categories, auth, roles,
    comments, media, notifications, audit_logs,
    frontend,
)

settings = get_settings()

# Configure logging on startup
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    import logging
    log = logging.getLogger(__name__)
    log.info(
        "Starting James Blog",
        extra={
            "environment": settings.ENVIRONMENT,
            "version": settings.PROJECT_VERSION,
            "debug": settings.DEBUG,
        },
    )
    yield
    log.info("Shutting down James Blog")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="A modular FastAPI platform for content and user management.",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url=None,  # We serve a custom ReDoc page below
    lifespan=lifespan,
)

# CORS Middleware (must be early)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# GZip compression for responses
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Trusted hosts (configure in production)
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.CORS_ORIGINS if settings.CORS_ORIGINS != ["*"] else ["*"],
    )

# Static files
static_dir = Path(__file__).resolve().parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# API Routers (under /api/v1)
app.include_router(roles.router, prefix=settings.API_V1_PREFIX)
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(posts.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(categories.router, prefix=settings.API_V1_PREFIX)
app.include_router(comments.router, prefix=settings.API_V1_PREFIX)
app.include_router(media.router, prefix=settings.API_V1_PREFIX)
app.include_router(notifications.router, prefix=settings.API_V1_PREFIX)
app.include_router(audit_logs.router, prefix=settings.API_V1_PREFIX)

# Frontend Router (no prefix — handles /, /posts, /auth/login, etc.)
app.include_router(frontend.router)


@app.get("/health")
async def health_check():
    """Simple health check for monitoring."""
    return {"status": "healthy", "service": "fastapi-platform"}


# Custom ReDoc endpoint with pinned CDN version
if settings.ENVIRONMENT == "development":

    @app.get("/redoc", include_in_schema=False)
    async def custom_redoc():
        """Render ReDoc documentation with a pinned CDN version."""
        return HTMLResponse(
            f"""<!DOCTYPE html>
<html>
<head>
    <title>{settings.PROJECT_NAME} - ReDoc</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    <style>
        body {{ margin: 0; padding: 0; }}
    </style>
</head>
<body>
    <noscript>ReDoc requires Javascript to function. Please enable it to browse the documentation.</noscript>
    <redoc spec-url="/openapi.json"></redoc>
    <script src="https://cdn.jsdelivr.net/npm/redoc@2.4.0/bundles/redoc.standalone.js"> </script>
</body>
</html>"""
        )
