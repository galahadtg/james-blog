"""Frontend router - HTML page rendering with Jinja2 templates."""

from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.core.dependencies import get_current_user_optional, get_current_user
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.models.media import Media
from app.services.user_service import UserService
from app.services.post_service import PostService
from app.services.comment_service import CommentService
from app.services.role_service import RoleService
from app.services.notification_service import NotificationService
from app.services.category_service import CategoryService

templates = Jinja2Templates(directory=Path(__file__).resolve().parent.parent / "templates")

router = APIRouter(tags=["Frontend"])


def _get_messages(request: Request):
    """Extract flash messages from query params."""
    messages = []
    error = request.query_params.get("error")
    success = request.query_params.get("success")
    if error:
        messages.append(("danger", error))
    if success:
        messages.append(("success", success))
    return messages


@router.get("/")
async def home(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
):
    """Render the home page."""
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "current_user": current_user, "messages": _get_messages(request)},
    )


# ---- Auth pages ---- #

@router.get("/auth/login")
async def login_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
):
    """Render the login page."""
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "current_user": current_user, "messages": _get_messages(request)},
    )


@router.post("/auth/login")
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Handle login form submission."""
    service = UserService(db)
    user = service.get_by_email(email)
    if not user or not verify_password(password, user.password_hash):
        return RedirectResponse(
            url="/auth/login?error=Invalid+email+or+password",
            status_code=303,
        )
    if not user.is_active:
        return RedirectResponse(
            url="/auth/login?error=Account+is+deactivated",
            status_code=303,
        )

    token = create_access_token(data={"sub": user.id})
    resp = RedirectResponse(url="/dashboard", status_code=303)
    resp.set_cookie(key="access_token", value=token, httponly=True, max_age=1800)
    return resp


@router.get("/auth/register")
async def register_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
):
    """Render the register page."""
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "current_user": current_user, "messages": _get_messages(request)},
    )


@router.post("/auth/register")
async def register_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Handle register form submission."""
    service = UserService(db)

    if service.get_by_username(username):
        return RedirectResponse(
            url="/auth/register?error=Username+already+taken",
            status_code=303,
        )
    if service.get_by_email(email):
        return RedirectResponse(
            url="/auth/register?error=Email+already+registered",
            status_code=303,
        )

    user = service.create(
        username=username,
        email=email,
        password_hash=hash_password(password),
        is_active=True,
    )
    role_service = RoleService(db)
    default_role = role_service.get_by_name("user")
    if default_role:
        service.update(user.id, role_id=default_role.id)

    token = create_access_token(data={"sub": user.id})
    resp = RedirectResponse(url="/dashboard?success=Account+created", status_code=303)
    resp.set_cookie(key="access_token", value=token, httponly=True, max_age=1800)
    return resp


@router.get("/auth/logout")
async def logout():
    """Log out by clearing the auth cookie."""
    resp = RedirectResponse(url="/?success=Logged+out", status_code=303)
    resp.delete_cookie("access_token")
    return resp


# ---- Post pages ---- #

@router.get("/posts")
async def post_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """Render the post listing page."""
    service = PostService(db)
    posts = service.get_published(skip=0, limit=50)
    return templates.TemplateResponse(
        "post_list.html",
        {"request": request, "current_user": current_user, "posts": posts, "messages": _get_messages(request)},
    )


@router.get("/posts/create")
async def create_post_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """Render the create post form."""
    if not current_user:
        return RedirectResponse(url="/auth/login?error=Please+log+in+first", status_code=303)
    if "post.create" not in current_user.permissions:
        return RedirectResponse(url="/posts?error=Permission+denied", status_code=303)
    categories = CategoryService(db).get_all()
    return templates.TemplateResponse(
        "post_create.html",
        {"request": request, "current_user": current_user, "categories": categories, "messages": _get_messages(request)},
    )


@router.post("/posts/create")
async def create_post_submit(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    excerpt: str | None = Form(default=None),
    category_id: int | None = Form(default=None),
    published: bool = Form(default=False),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """Handle create post form submission."""
    if not current_user:
        return RedirectResponse(url="/auth/login?error=Please+log+in+first", status_code=303)
    if "post.create" not in current_user.permissions:
        return RedirectResponse(url="/posts?error=Permission+denied", status_code=303)

    service = PostService(db)
    post = service.create(
        title=title,
        content=content,
        excerpt=excerpt or None,
        published=published,
        author_id=current_user.id,
        category_id=category_id,
    )
    return RedirectResponse(url=f"/posts/{post.slug}?success=Post+created", status_code=303)


@router.get("/posts/{slug}")
async def post_detail(
    request: Request,
    slug: str,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """Render a single post page with comments."""
    from sqlalchemy import select
    service = PostService(db)
    post = service.get_by_slug(slug)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Get approved comments
    comments = (
        db.execute(
            select(Comment)
            .where(Comment.post_id == post.id)
            .where(Comment.status == "approved")
            .where(Comment.is_removed == False)
            .order_by(Comment.created_at.asc())
        )
        .scalars()
        .all()
    )

    return templates.TemplateResponse(
        "post_detail.html",
        {
            "request": request,
            "current_user": current_user,
            "post": post,
            "comments": comments,
            "messages": _get_messages(request),
        },
    )


@router.post("/posts/{post_id}/comments")
async def add_comment(
    request: Request,
    post_id: int,
    content: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """Handle comment form submission."""
    if not current_user:
        return RedirectResponse(url="/auth/login?error=Please+log+in+first", status_code=303)

    from app.services.comment_service import CommentService
    from app.services.notification_service import NotificationService

    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment_service = CommentService(db)
    comment = comment_service.create(
        content=content,
        post_id=post_id,
        author_id=current_user.id,
        status="approved",
    )

    # Notify post author
    if post.author_id != current_user.id:
        NotificationService(db).create_notification(
            user_id=post.author_id,
            type="new_comment",
            message=f"{current_user.username} commented on \"{post.title[:50]}\"",
        )

    return RedirectResponse(
        url=f"/posts/{post.slug}#comment-{comment.id}?success=Comment+posted",
        status_code=303,
    )


# ---- Dashboard ---- #

@router.get("/dashboard")
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """Render the user dashboard. Redirects to login if not authenticated."""
    if not current_user:
        return RedirectResponse(url="/auth/login?error=Please+log+in+first", status_code=303)
    post_service = PostService(db)
    comment_service = CommentService(db)
    notify_service = NotificationService(db)
    media_count = db.query(Media).count()

    stats = {
        "post_count": post_service.count(),
        "comment_count": comment_service.count(),
        "unread_notifications": notify_service.get_unread_count(current_user.id),
        "media_count": media_count,
    }

    notifications = notify_service.get_user_notifications(current_user.id, limit=10)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "current_user": current_user,
            "stats": stats,
            "notifications": notifications,
            "messages": _get_messages(request),
        },
    )
