"""Posts router - demonstrates FastAPI fundamentals.

This router teaches:
  - Path parameters:   /posts/{post_id}
  - Query parameters:  /posts/?skip=0&limit=10
  - Request bodies:    POST /posts/  with JSON data
  - Response models:   Controlling what data is returned
  - HTTP status codes: 200, 201, 404, etc.
  - Pydantic validation

For now, posts are stored in memory. We'll add a real database in Phase 3.
"""

from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, HTTPException, status

from app.schemas.post import PostCreate, PostResponse, PostUpdate

router = APIRouter(prefix="/posts", tags=["Posts"])

# ---------------------------------------------------------------------------
# In-memory storage (temporary - will be replaced by database in Phase 3)
# ---------------------------------------------------------------------------
_db: list[dict] = []
_next_id: int = 1


def _now() -> datetime:
    """Return the current time with timezone info."""
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# GET /posts/
#   Demonstrates: query parameters, list response, status codes
# ---------------------------------------------------------------------------


@router.get("/", response_model=List[PostResponse], status_code=status.HTTP_200_OK)
async def get_posts(skip: int = 0, limit: int = 10, search: str | None = None):
    """Get a list of posts with pagination.

    Query parameters (try them in Swagger UI at /docs):
      - skip:  Number of posts to skip (default: 0)
      - limit: Maximum posts to return (default: 10)
      - search: Optional text to search in titles

    FastAPI automatically:
      1. Reads query params from the URL
      2. Validates types (int, str, etc.)
      3. Returns 422 if validation fails
    """
    posts = _db

    # Filter by search term if provided
    if search:
        posts = [p for p in posts if search.lower() in p["title"].lower()]

    # Apply pagination (skip then limit)
    return posts[skip : skip + limit]


# ---------------------------------------------------------------------------
# GET /posts/{post_id}
#   Demonstrates: path parameters, error handling, 404 status
# ---------------------------------------------------------------------------


@router.get("/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
async def get_post(post_id: int):
    """Get a single post by its ID.

    Path parameters are declared in the URL pattern and function signature.
    FastAPI automatically:
      1. Extracts the value from the URL path
      2. Validates it's an integer
      3. Passes it to the function
    """
    for post in _db:
        if post["id"] == post_id:
            return post

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Post with id {post_id} not found",
    )


# ---------------------------------------------------------------------------
# POST /posts/
#   Demonstrates: request bodies, 201 Created, Pydantic validation
# ---------------------------------------------------------------------------


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post_data: PostCreate):
    """Create a new post.

    FastAPI automatically:
      1. Reads the JSON request body
      2. Validates it against the PostCreate schema
      3. Returns 422 with details if validation fails

    Try sending invalid data (empty title) to see validation in action.
    """
    global _next_id

    new_post = {
        "id": _next_id,
        "title": post_data.title,
        "content": post_data.content,
        "published": post_data.published,
        "created_at": _now(),
        "updated_at": _now(),
    }
    _db.append(new_post)
    _next_id += 1

    return new_post


# ---------------------------------------------------------------------------
# PUT /posts/{post_id}
#   Demonstrates: full update (replace entire resource)
# ---------------------------------------------------------------------------


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, post_data: PostUpdate):
    """Update an existing post (partial update with PATCH semantics).

    All fields are optional in PostUpdate, so clients can send
    only the fields they want to change.
    """
    for post in _db:
        if post["id"] == post_id:
            if post_data.title is not None:
                post["title"] = post_data.title
            if post_data.content is not None:
                post["content"] = post_data.content
            if post_data.published is not None:
                post["published"] = post_data.published
            post["updated_at"] = _now()
            return post

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Post with id {post_id} not found",
    )


# ---------------------------------------------------------------------------
# DELETE /posts/{post_id}
#   Demonstrates: delete operations, 204 No Content
# ---------------------------------------------------------------------------


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int):
    """Delete a post by its ID.

    Returns 204 No Content on success (no response body).
    """
    for i, post in enumerate(_db):
        if post["id"] == post_id:
            _db.pop(i)
            return  # 204 No Content - no body

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Post with id {post_id} not found",
    )
