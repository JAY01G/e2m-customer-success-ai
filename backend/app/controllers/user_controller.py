"""User Management HTTP Controller.

Delegates user CRUD actions, pagination formatting, and role updates to UserService.
"""

import uuid
from sqlalchemy.orm import Session
from app.helpers import api_response, paginated_api_response
from app.schemas import (
    APIResponse,
    PaginatedData,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.schemas.user import UserRoleUpdate
from app.services.user_service import UserService


class UserController:
    """Controller handling user management HTTP endpoints."""

    @staticmethod
    def get_users(page: int, page_size: int, db: Session) -> APIResponse[PaginatedData[UserResponse]]:
        """Retrieve paginated list of user accounts.

        Args:
            page: 1-based page index.
            page_size: Maximum users per page.
            db: Database session.

        Returns:
            APIResponse[PaginatedData[UserResponse]]: Paginated user response envelope.
        """
        service = UserService(db)
        items, total = service.get_all(page=page, page_size=page_size)
        resp_items = [UserResponse.model_validate(u) for u in items]
        return paginated_api_response(
            items=resp_items,
            total=total,
            page=page,
            page_size=page_size,
            message="Users retrieved successfully",
        )

    @staticmethod
    def get_user(user_id: uuid.UUID, db: Session) -> APIResponse[UserResponse]:
        """Retrieve single user details by UUID.

        Args:
            user_id: User UUID.
            db: Database session.

        Returns:
            APIResponse[UserResponse]: User response envelope.
        """
        service = UserService(db)
        user = service.get_by_id(user_id)
        return api_response(
            data=UserResponse.model_validate(user),
            message="User retrieved successfully",
        )

    @staticmethod
    def create_user(req: UserCreate, db: Session) -> APIResponse[UserResponse]:
        """Create a new user account.

        Args:
            req: User creation schema.
            db: Database session.

        Returns:
            APIResponse[UserResponse]: Created user response envelope.
        """
        service = UserService(db)
        user = service.create(req)
        return api_response(
            data=UserResponse.model_validate(user),
            message="User created successfully",
        )

    @staticmethod
    def update_user(user_id: uuid.UUID, req: UserUpdate, db: Session) -> APIResponse[UserResponse]:
        """Update fields on an existing user account.

        Args:
            user_id: User UUID.
            req: User update schema.
            db: Database session.

        Returns:
            APIResponse[UserResponse]: Updated user response envelope.
        """
        service = UserService(db)
        user = service.update(user_id, req)
        return api_response(
            data=UserResponse.model_validate(user),
            message="User updated successfully",
        )

    @staticmethod
    def update_user_role(user_id: uuid.UUID, req: UserRoleUpdate, db: Session) -> APIResponse[UserResponse]:
        """Update the assigned role of a user.

        Args:
            user_id: User UUID.
            req: Role update schema.
            db: Database session.

        Returns:
            APIResponse[UserResponse]: Updated user response envelope.
        """
        service = UserService(db)
        user = service.update_role(user_id, req)
        return api_response(
            data=UserResponse.model_validate(user),
            message="User role updated successfully",
        )

    @staticmethod
    def delete_user(user_id: uuid.UUID, db: Session) -> APIResponse[None]:
        """Delete a user account.

        Args:
            user_id: User UUID.
            db: Database session.

        Returns:
            APIResponse[None]: Deletion confirmation envelope.
        """
        service = UserService(db)
        service.delete(user_id)
        return api_response(
            data=None,
            message="User deleted successfully",
        )

