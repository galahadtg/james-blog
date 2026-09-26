"""Media model for file uploads and management."""

from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class Media(TimestampMixin, Base):
    """Uploaded media file metadata.

    Files are stored on disk; this table tracks metadata.
    Supports images, documents, videos, and other file types.
    """

    __tablename__ = "media"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    filepath: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Foreign Keys
    uploader_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Relationships
    uploader = relationship("User")

    def __repr__(self) -> str:
        return f"<Media {self.original_filename} ({self.size} bytes)>"
