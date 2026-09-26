"""Comments router - REST API for comment management and moderation."""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.database.session import get_db
from app.models.comment import Comment
from app.models.post import Post
from app.schemas.comment import (
    CommentCreate,
    CommentModerate,
    CommentResponse,
    CommentUpdate,
)
from app.services.comment_service import CommentService
from app.core.authorization import require_permission, Perm
from app.core.dependencies import get_current_user
from app.models.user import User
from sqlalchemy.orm import Session

router = APIRouter(prefix="/comments", tags=["Comments"])


@router.get("/", response_model=list[CommentResponse])
async def get_comments(
    post_id: int | None = Query(None, description="Filter by post"),
    status_filter: str | None = Query(None, alias="status", description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """List comments. Public users see only approved comments."""
    service = CommentService(db)

    if post_id:
        # Public listing — only approved comments
        return service.get_by_post(post_id, skip=skip, limit=limit, approved_only=True)

    # Filtered listing (requires auth handled by status param usage)
    if status_filter:
        if status_filter == "pending":
            # Will be caught by 403 if user lacks permission
            current_user = Depends(require_permission(Perm.COMMENT_MODERATE))
            return service.get_pending(skip=skip, limit=limit)

    return service.get_all(skip=skip, limit=limit)


@router.get("/pending", response_model=list[CommentResponse])
async def get_pending_comments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Perm.COMMENT_MODERATE)),
):
    """List all comments pending moderation."""
    service = CommentService(db)
    return service.get_pending(skip=skip, limit=limit)


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(
    comment_id: int,
    db: Session = Depends(get_db),
):
    """Get a single comment by ID."""
    service = CommentService(db)
    comment = service.get(comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with id {comment_id} not found",
        )
    return comment


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Perm.COMMENT_CREATE)),
):
    """Create a new comment on a post."""

    # Verify the post exists
    post = db.get(Post, comment_data.post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {comment_data.post_id} not found",
        )

    # If replying, verify parent comment exists
    if comment_data.parent_id:
        parent = db.get(Comment, comment_data.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent comment with id {comment_data.parent_id} not found",
            )

    service = CommentService(db)
    comment = service.create(
        content=comment_data.content,
        post_id=comment_data.post_id,
        parent_id=comment_data.parent_id,
        author_id=current_user.id,
        status="approved",  # Auto-approve for now; change to "pending" if moderation needed
    )

    # Auto-create notification
    from app.services.notification_service import NotificationService
    notify = NotificationService(db)

    if comment_data.parent_id:
        # Reply to a comment — notify the parent comment author
        parent_comment = db.get(Comment, comment_data.parent_id)
        if parent_comment and parent_comment.author_id != current_user.id:
            notify.create_notification(
                user_id=parent_comment.author_id,
                type="comment_reply",
                message=f"{current_user.username} replied to your comment on \"{post.title[:50]}\"",
                link=f"/posts/{post.slug}#comment-{comment.id}",
            )
    elif post.author_id != current_user.id:
        # New comment on a post — notify the post author
        notify.create_notification(
            user_id=post.author_id,
            type="new_comment",
            message=f"{current_user.username} commented on \"{post.title[:50]}\"",
            link=f"/posts/{post.slug}#comment-{comment.id}",
        )

    return comment


@router.patch("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Perm.COMMENT_UPDATE)),
):
    """Update a comment (content edit)."""
    service = CommentService(db)
    comment = service.get(comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with id {comment_id} not found",
        )

    # Users can only edit their own comments (unless they have admin access)
    if comment.author_id != current_user.id and Perm.ADMIN_ACCESS not in current_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own comments",
        )

    updated = service.update(
        comment_id,
        content=comment_data.content,
        status="pending",  # Re-queue for moderation on edit
    )
    return updated


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Perm.COMMENT_DELETE)),
):
    """Soft-delete a comment (marks as removed)."""
    service = CommentService(db)
    comment = service.get(comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with id {comment_id} not found",
        )
    service.remove(comment_id)
    return


@router.post("/{comment_id}/moderate", response_model=CommentResponse)
async def moderate_comment(
    comment_id: int,
    moderation: CommentModerate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Perm.COMMENT_MODERATE)),
):
    """Approve or reject a comment."""
    service = CommentService(db)
    comment = service.moderate(comment_id, moderation.status, current_user.id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with id {comment_id} not found",
        )
    return comment
