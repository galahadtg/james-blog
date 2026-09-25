"""Posts router - REST API for content management.

Now backed by PostgreSQL via the service layer.
Keeps the same API surface but with proper database persistence.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.post import PostCreate, PostResponse, PostUpdate
from app.services.post_service import PostService

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=List[PostResponse])
async def get_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = None,
    status_filter: str | None = Query(None, alias="status"),
    author_id: int | None = None,
    category_id: int | None = None,
    published_only: bool = False,
    db: Session = Depends(get_db),
):
    """Get posts with filtering and pagination.

    Supports:
      - search: full-text search in title/content
      - status: filter by draft/published
      - author_id: filter by author
      - category_id: filter by category
      - published_only: shortcut for published posts only
    """
    service = PostService(db)

    if published_only:
        return service.get_published(skip=skip, limit=limit)

    if search:
        return service.search(search, skip=skip, limit=limit)

    if author_id:
        return service.get_by_author(author_id)

    if category_id:
        return service.get_by_category(category_id)

    return service.get_all(skip=skip, limit=limit)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get a single post by ID."""
    service = PostService(db)
    post = service.get(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found",
        )
    return post


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    author_id: int = Query(..., description="Author user ID"),
    db: Session = Depends(get_db),
):
    """Create a new post. Requires author_id."""
    service = PostService(db)
    return service.create(
        title=post_data.title,
        content=post_data.content,
        excerpt=post_data.excerpt,
        published=post_data.published,
        author_id=author_id,
        category_id=post_data.category_id,
    )


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    db: Session = Depends(get_db),
):
    """Update a post (partial update)."""
    service = PostService(db)
    post = service.update(
        post_id,
        title=post_data.title,
        content=post_data.content,
        excerpt=post_data.excerpt,
        category_id=post_data.category_id,
    )
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found",
        )
    return post


@router.post("/{post_id}/publish", response_model=PostResponse)
async def publish_post(post_id: int, db: Session = Depends(get_db)):
    """Publish a post (sets status to 'published' with timestamp)."""
    service = PostService(db)
    post = service.publish(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found",
        )
    return post


@router.post("/{post_id}/unpublish", response_model=PostResponse)
async def unpublish_post(post_id: int, db: Session = Depends(get_db)):
    """Unpublish a post (reverts to draft)."""
    service = PostService(db)
    post = service.unpublish(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found",
        )
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    """Delete a post."""
    service = PostService(db)
    deleted = service.delete(post_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found",
        )
    return
