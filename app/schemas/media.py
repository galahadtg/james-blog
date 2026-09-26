"""Pydantic schemas for Media requests and responses."""

from datetime import datetime
from pydantic import BaseModel


class MediaResponse(BaseModel):
    """Schema for returning media metadata in API responses."""

    id: int
    filename: str
    original_filename: str
    filepath: str
    mime_type: str
    size: int
    is_public: bool
    uploader_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MediaUpdate(BaseModel):
    """Schema for updating media metadata."""

    is_public: bool | None = None
