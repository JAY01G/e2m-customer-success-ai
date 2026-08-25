"""Authentication Dependencies.

Extracts, validates, and decodes JWT bearer tokens to inject authenticated User entities into endpoints.
"""

import uuid
from typing import Optional
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.database.dependencies import get_db
from app.exceptions.custom_exceptions import UnauthorizedException
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.utils.security import decode_token

security = HTTPBearer(
    auto_error=False,
    scheme_name="JWTBearer",
    description="Enter your JWT Bearer access token (e.g. Bearer eyJhbGciOi...). Obtain via /api/v1/auth/login.",
    bearerFormat="JWT",
)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Extract and validate the JWT bearer token from the Authorization header.

    Args:
        credentials: HTTP bearer credentials.
        db: Scoped database session.

    Returns:
        User: Authenticated User ORM model.

    Raises:
        UnauthorizedException: If token is missing, expired, invalid, or user is inactive/nonexistent.
    """
    if not credentials or not credentials.credentials:
        raise UnauthorizedException("Authentication token is missing")

    token = credentials.credentials
    payload = decode_token(token, expected_type="access")
    user_id_str = payload.get("sub")

    if not user_id_str:
        raise UnauthorizedException("Invalid token subject")

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise UnauthorizedException("Invalid user ID format in token")

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_uuid)

    if not user:
        raise UnauthorizedException("User no longer exists")

    if not user.is_active:
        raise UnauthorizedException("User account is inactive")

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure that the authenticated user is currently active.

    Args:
        current_user: User entity resolved from get_current_user.

    Returns:
        User: Active User ORM model.

    Raises:
        UnauthorizedException: If user account is deactivated.
    """
    if not current_user.is_active:
        raise UnauthorizedException("User account is inactive")
    return current_user

