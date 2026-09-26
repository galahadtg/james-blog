"""Media router - REST API for file uploads and management."""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path

from app.database.session import get_db
from app.models.media import Media
from app.schemas.media import MediaResponse, MediaUpdate
from app.services.media_service import MediaService
from app.core.authorization import require_permission, Perm
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/media", tags=["Media"])


@router.get("/", response_model=list[MediaResponse])
async def list_media(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    mime_filter: str | None = Query(None, alias="mime_type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Perm.MEDIA_READ)),
):
    """List all media files with pagination and optional MIME type filter."""
    service = MediaService(db)

    if mime_filter:
        return (
            db.query(Media)
            .filter(Media.mime_type.like(f"{mime_filter}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )

    return service.get_all(skip=skip, limit=limit)


@router.get("/{media_id}", response_model=MediaResponse)
async def get_media(
    media_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Perm.MEDIA_READ)),
):
    """Get a single media item's metadata."""
    service = MediaService(db)
    media = service.get(media_id)
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Media with id {media_id} not found",
        )
    return media


@router.post("/upload", response_model=MediaResponse, status_code=status.HTTP_201_CREATED)
async def upload_media(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Perm.MEDIA_CREATE)),
):
    """Upload a file. Stores on disk and returns metadata."""
    service = MediaService(db)
    return service.save_upload(file, current_user.id)


@router.get("/{media_id}/download")
async def download_media(
    media_id: int,
    db: Session = Depends(get_db),
):
    """Download/serve a media file."""
    service = MediaService(db)
    media = service.get(media_id)
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found",
        )

    filepath = Path(media.filepath)
    if not filepath.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk",
        )

    return FileResponse(
        path=str(filepath),
        media_type=media.mime_type,
        filename=media.original_filename,
    )


@router.patch("/{media_id}", response_model=MediaResponse)
async def update_media(
    media_id: int,
    data: MediaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Perm.MEDIA_UPDATE)),
):
    """Update media metadata (e.g., visibility)."""
    service = MediaService(db)
    media = service.update(media_id, is_public=data.is_public)
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Media with id {media_id} not found",
        )
    return media


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(
    media_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Perm.MEDIA_DELETE)),
):
    """Delete a media file from disk and database."""
    service = MediaService(db)
    deleted = service.delete_file(media_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Media with id {media_id} not found",
        )
    return
