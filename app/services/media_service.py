"""Media service for file upload handling."""

import os
import uuid
from pathlib import Path

from fastapi import UploadFile, HTTPException, status

from app.core.config import get_settings
from app.models.media import Media
from app.services.base import BaseService

settings = get_settings()


class MediaService(BaseService[Media]):
    """Service for media/file management."""

    def __init__(self, db):
        super().__init__(db, Media)

    def save_upload(self, file: UploadFile, uploader_id: int) -> Media:
        """Save an uploaded file to disk and create a media record."""
        # Validate extension
        ext = Path(file.filename).suffix.lower() if file.filename else ""
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File extension '{ext}' is not allowed. "
                       f"Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}",
            )

        # Read content
        content = file.file.read()
        file_size = len(content)

        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE // (1024*1024)} MB.",
            )

        # Create storage path
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Unique filename to prevent collisions
        unique_name = f"{uuid.uuid4().hex}{ext}"
        filepath = upload_dir / unique_name

        # Write to disk
        filepath.write_bytes(content)

        # Create database record
        return self.create(
            filename=unique_name,
            original_filename=file.filename,
            filepath=str(filepath),
            mime_type=file.content_type or "application/octet-stream",
            size=file_size,
            uploader_id=uploader_id,
        )

    def delete_file(self, media_id: int) -> bool:
        """Delete a media record and its file from disk."""
        media = self.get(media_id)
        if not media:
            return False

        # Delete file from disk
        filepath = Path(media.filepath)
        if filepath.exists():
            filepath.unlink()

        # Delete database record
        return super().delete(media_id)
