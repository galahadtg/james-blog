"""Logging configuration for the FastAPI Platform.

In production, logs are structured JSON for integration with
log aggregation services (Datadog, ELK, CloudWatch, etc.).
"""

import logging
import sys
from pathlib import Path

from app.core.config import get_settings

settings = get_settings()


def setup_logging() -> None:
    """Configure application-wide logging.

    - Development: human-readable console output
    - Production: JSON-structured logs for log aggregation
    """
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # Root logger
    root = logging.getLogger()
    root.setLevel(log_level)

    # Remove default handlers
    root.handlers.clear()

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(log_level)

    if settings.ENVIRONMENT == "development":
        fmt = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        # Structured JSON format for production
        fmt = logging.Formatter(
            '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s",'
            '"line":%(lineno)d,"message":"%(message)s"}',
            datefmt="%Y-%m-%dT%H:%M:%S",
        )

    console.setFormatter(fmt)
    root.addHandler(console)

    # Set third-party loggers to WARNING in production
    if settings.ENVIRONMENT != "development":
        for logger_name in ("uvicorn", "uvicorn.access", "sqlalchemy.engine"):
            logging.getLogger(logger_name).setLevel(logging.WARNING)

    root.info(
        "Logging configured",
        extra={"environment": settings.ENVIRONMENT, "log_level": log_level},
    )
