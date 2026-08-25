"""User Administration API Router.

Mounts administrative endpoints for listing, creating, reading, updating,
role-assigning, and deleting user accounts. Protected by Admin RBAC guards.
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.controllers.user_controller import UserController
from app.database.dependencies import get_db
from app.dependencies.permissions import require_admin
from app.models.user import User
from app.schemas import (
    APIResponse,
    PaginatedData,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.schemas.user import UserRoleUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "",
    response_model=APIResponse[PaginatedData[UserResponse]],
    status_code=status.HTTP_200_OK,
    summary="List all users (Admin only)",
    response_description="Paginated list of system user accounts",
)
def get_users(
    page: int = Query(1, ge=1, description="1-based page index"),
    page_size: int = Query(50, ge=1, le=100, description="Items returned per page (max 100)"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Retrieve paginated list of all system users.

    Args:
        page: Page number starting at 1.
        page_size: Items per page.
        current_user: Authenticated Admin user.
        db: Scoped database session.

    Returns:
        APIResponse[PaginatedData[UserResponse]]: Paginated user response envelope.
    """
    return UserController.get_users(page=page, page_size=page_size, db=db)


@router.post(
    "",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user (Admin only)",
    response_description="Newly created user profile details",
)
def create_user(
    req: UserCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create a new operator account with role and password.

    Args:
        req: User creation payload.
        current_user: Authenticated Admin user.
        db: Scoped database session.

    Returns:
        APIResponse[UserResponse]: Created user envelope.
    """
    return UserController.create_user(req=req, db=db)


@router.get(
    "/{user_id}",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Get user by ID (Admin only)",
    response_description="User account profile and RBAC role",
)
def get_user(
    user_id: uuid.UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Retrieve details of a single user account by UUID.

    Args:
        user_id: Target user UUID.
        current_user: Authenticated Admin user.
        db: Scoped database session.

    Returns:
        APIResponse[UserResponse]: User details envelope.
    """
    return UserController.get_user(user_id=user_id, db=db)


@router.patch(
    "/{user_id}",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Update user details (Admin only)",
    response_description="Updated user profile details",
)
def update_user(
    user_id: uuid.UUID,
    req: UserUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update profile attributes on a user account.

    Args:
        user_id: Target user UUID.
        req: Update fields payload.
        current_user: Authenticated Admin user.
        db: Scoped database session.

    Returns:
        APIResponse[UserResponse]: Updated user envelope.
    """
    return UserController.update_user(user_id=user_id, req=req, db=db)


@router.patch(
    "/{user_id}/role",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Update user role (Admin only)",
    response_description="User profile with updated RBAC role",
)
def update_user_role(
    user_id: uuid.UUID,
    req: UserRoleUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update the RBAC role assigned to a user account.

    Args:
        user_id: Target user UUID.
        req: Role update payload.
        current_user: Authenticated Admin user.
        db: Scoped database session.

    Returns:
        APIResponse[UserResponse]: Updated user envelope.
    """
    return UserController.update_user_role(user_id=user_id, req=req, db=db)


@router.delete(
    "/{user_id}",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Delete user (Admin only)",
    response_description="User account deletion confirmation",
)
def delete_user(
    user_id: uuid.UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete a user account from the system.

    Args:
        user_id: Target user UUID to remove.
        current_user: Authenticated Admin user.
        db: Scoped database session.

    Returns:
        APIResponse[None]: Deletion confirmation envelope.
    """
    return UserController.delete_user(user_id=user_id, db=db)


