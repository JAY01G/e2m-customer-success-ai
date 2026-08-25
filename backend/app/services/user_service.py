"""User Profile and Management Service.

Implements business logic for operator accounts, profile modification,
password resetting, and administrative role assignments.
"""

import uuid
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.config.logging import logger
from app.exceptions.custom_exceptions import ConflictException, NotFoundException
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserRoleUpdate, UserUpdate
from app.utils.security import get_password_hash
from app.utils.validators import validate_password_strength


class UserService:
    """Service managing operator accounts, profiles, and administrative roles."""

    def __init__(self, db: Session):
        """Initialize UserService with database session and UserRepository.

        Args:
            db: Scoped SQLAlchemy database session.
        """
        self.db = db
        self.user_repo = UserRepository(db)

    def get_by_id(self, user_id: uuid.UUID) -> User:
        """Fetch user by UUID or raise NotFoundException.

        Args:
            user_id: Unique UUID of the user.

        Returns:
            User: User model instance.

        Raises:
            NotFoundException: If user with given UUID is not found.
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with ID {user_id} not found")
        return user

    def get_by_email(self, email: str) -> Optional[User]:
        """Fetch user by email address.

        Args:
            email: Email address string.

        Returns:
            Optional[User]: User model instance or None.
        """
        return self.user_repo.get_by_email(email)

    def get_all(self, page: int = 1, page_size: int = 50) -> Tuple[List[User], int]:
        """Fetch paginated list of user accounts.

        Args:
            page: 1-based page index.
            page_size: Maximum users per page.

        Returns:
            Tuple[List[User], int]: User entities list and total record count.
        """
        offset = (page - 1) * page_size
        return self.user_repo.get_all(offset=offset, limit=page_size)

    def create(self, data: UserCreate) -> User:
        """Create and persist a new user record.

        Args:
            data: User creation schema.

        Returns:
            User: Newly created User model.

        Raises:
            ConflictException: If email already exists.
        """
        existing = self.user_repo.get_by_email(data.email)
        if existing:
            raise ConflictException(f"User with email '{data.email}' already exists")

        validate_password_strength(data.password)
        hashed_password = get_password_hash(data.password)

        new_user = User(
            name=data.name.strip(),
            email=data.email.lower().strip(),
            hashed_password=hashed_password,
            role=data.role,
            is_active=data.is_active,
        )
        created = self.user_repo.create(new_user)
        logger.info(f"User created: {created.email} (Role: {created.role}) [ID: {created.id}]")
        return created

    def update(self, user_id: uuid.UUID, data: UserUpdate) -> User:
        """Update fields on an existing user account.

        Args:
            user_id: Unique UUID of the user.
            data: User update schema.

        Returns:
            User: Updated User model.

        Raises:
            ConflictException: If updated email is already taken by another account.
        """
        user = self.get_by_id(user_id)

        if data.email and data.email.lower() != user.email.lower():
            existing = self.user_repo.get_by_email(data.email)
            if existing and existing.id != user_id:
                raise ConflictException(f"Email '{data.email}' is already taken")
            user.email = data.email.lower().strip()

        if data.name is not None:
            user.name = data.name.strip()

        if data.role is not None:
            user.role = data.role

        if data.is_active is not None:
            user.is_active = data.is_active

        if data.password:
            validate_password_strength(data.password)
            user.hashed_password = get_password_hash(data.password)

        updated = self.user_repo.update(user)
        logger.info(f"User updated: {updated.email} [ID: {updated.id}]")
        return updated

    def update_role(self, user_id: uuid.UUID, data: UserRoleUpdate) -> User:
        """Update the RBAC role of a user.

        Args:
            user_id: Unique UUID of the user.
            data: Role update schema.

        Returns:
            User: Updated User model.
        """
        user = self.get_by_id(user_id)
        user.role = data.role
        updated = self.user_repo.update(user)
        logger.info(f"User role updated: {updated.email} -> {data.role} [ID: {updated.id}]")
        return updated

    def delete(self, user_id: uuid.UUID) -> None:
        """Delete a user account.

        Args:
            user_id: Unique UUID of the user to delete.
        """
        user = self.get_by_id(user_id)
        self.user_repo.delete(user)
        logger.info(f"User deleted: {user.email} [ID: {user_id}]")

