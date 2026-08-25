"""User Data Access Repository.

Implements database queries and persistence operations for the User entity using SQLAlchemy 2.0.
"""

import uuid
from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.user import User


class UserRepository:
    """Repository handling database operations for User accounts."""

    def __init__(self, db: Session):
        """Initialize repository with an active SQLAlchemy database session.

        Args:
            db: Scoped database session.
        """
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Fetch a single user by primary UUID.

        Args:
            user_id: Unique UUID of the user.

        Returns:
            Optional[User]: User ORM instance if found, else None.
        """
        stmt = select(User).where(User.id == user_id)
        return self.db.scalars(stmt).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Fetch a single user by case-insensitive email address.

        Args:
            email: User's email string.

        Returns:
            Optional[User]: User ORM instance if found, else None.
        """
        stmt = select(User).where(func.lower(User.email) == email.lower().strip())
        return self.db.scalars(stmt).first()

    def get_all(self, offset: int = 0, limit: int = 50) -> Tuple[List[User], int]:
        """Retrieve paginated list of all users ordered by creation date descending.

        Args:
            offset: Number of items to skip.
            limit: Maximum number of items to return.

        Returns:
            Tuple[List[User], int]: List of user entities and total record count.
        """
        total = self.db.scalar(select(func.count(User.id))) or 0
        stmt = select(User).order_by(User.created_at.desc()).offset(offset).limit(limit)
        items = list(self.db.scalars(stmt).all())
        return items, total

    def create(self, user: User) -> User:
        """Persist and refresh a new user entity in the database.

        Args:
            user: Unpersisted User model instance.

        Returns:
            User: Committed and refreshed User model instance.
        """
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User) -> User:
        """Commit updates to an existing user entity.

        Args:
            user: Modified User model instance.

        Returns:
            User: Refreshed User model instance.
        """
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        """Delete a user entity from the database.

        Args:
            user: User model instance to remove.
        """
        self.db.delete(user)
        self.db.commit()

