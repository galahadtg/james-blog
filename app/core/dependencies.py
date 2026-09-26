"""FastAPI dependencies for authentication and authorization.

Key dependencies:
  - get_current_user: Extracts and validates the JWT, returns the User
  - require_active_user: Ensures the user account is active
"""

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.core.security import decode_token
from app.services.user_service import UserService

# Bearer token extractor - reads the Authorization header
# Automatically returns 403 if no token is present
security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency that extracts the current user from a JWT.

    Usage in protected routes:
        @router.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            ...

    Returns 401 if:
      - No token provided
      - Token is invalid or expired
      - User doesn't exist or is inactive
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please provide a Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str: str | None = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
        )

    user_id = int(user_id_str)

    service = UserService(db)
    user = service.get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )

    return user


async def require_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency that ensures the authenticated user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated.",
        )
    return current_user


async def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db),
) -> User | None:
    """Optional auth dependency — returns None instead of 401 if no token.

    Checks both the Authorization header and the access_token cookie.
    Use for pages that work for both guests and logged-in users.
    """
    # Try cookie first (browser-based auth)
    token_str = request.cookies.get("access_token")

    # Fall back to Authorization header
    if not token_str:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token_str = auth_header[7:]

    if not token_str:
        return None

    payload = decode_token(token_str)
    if payload is None:
        return None

    user_id_str = payload.get("sub")
    if user_id_str is None:
        return None

    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        return None

    service = UserService(db)
    return service.get(user_id)
