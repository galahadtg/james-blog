"""FastAPI Platform - Main Application Entry Point.

A modular FastAPI application for Business Content & User Management.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers import posts

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="A modular FastAPI platform for content and user management.",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
)

# Include Routers
app.include_router(posts.router, prefix=settings.API_V1_PREFIX)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint - verifies the application is running."""
    return {
        "message": "Welcome to the FastAPI Platform",
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Simple health check for monitoring."""
    return {"status": "healthy", "service": "fastapi-platform"}
