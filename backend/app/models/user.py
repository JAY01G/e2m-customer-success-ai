"""User and Authentication ORM Models.

Defines the User entity representing system operators (Admins, CSMs, Viewers),
including role-based access control (RBAC) levels and relational links to managed customers.
"""

import enum
from typing import List, TYPE_CHECKING
from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.interaction import Interaction


class UserRole(str, enum.Enum):
    """Enumeration of user access and permission tiers."""

    ADMIN = "ADMIN"
    CUSTOMER_SUCCESS_MANAGER = "CUSTOMER_SUCCESS_MANAGER"
    VIEWER = "VIEWER"


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """User database model representing application operators.

    Attributes:
        id: Unique UUID identifier.
        name: Operator full name.
        email: Unique login email address.
        hashed_password: Bcrypt hashed password string.
        role: User role governing RBAC access permissions.
        is_active: Active account status flag.
        customers: List of customers managed by this user.
        interactions: List of meeting/interaction logs recorded by this user.
        created_at: UTC timestamp of creation.
        updated_at: UTC timestamp of last update.
    """

    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", create_type=False),
        default=UserRole.CUSTOMER_SUCCESS_MANAGER,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    customers: Mapped[List["Customer"]] = relationship(
        "Customer", back_populates="owner", cascade="all, delete-orphan"
    )
    interactions: Mapped[List["Interaction"]] = relationship(
        "Interaction", back_populates="user"
    )

    def __repr__(self) -> str:
        """Return developer-friendly string representation of the User instance."""
        return f"<User id={self.id} email={self.email} role={self.role}>"

