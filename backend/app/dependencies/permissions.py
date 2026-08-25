"""Role-Based Access Control (RBAC) Permission Dependencies.

Provides dependency factories and shortcuts to enforce user role restrictions on API routes.
"""

from typing import Callable, List
from fastapi import Depends
from app.dependencies.auth import get_current_active_user
from app.exceptions.custom_exceptions import ForbiddenException
from app.models.user import User, UserRole


def require_roles(*allowed_roles: UserRole) -> Callable[[User], User]:
    """Dependency factory checking that current user has one of the required roles.

    Args:
        *allowed_roles: Variable number of allowed UserRole enums.

    Returns:
        Callable[[User], User]: FastAPI dependency enforcing role checks.
    """

    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            role_names = [r.value for r in allowed_roles]
            raise ForbiddenException(
                f"Action requires one of the following roles: {', '.join(role_names)}. Current role: {current_user.role.value}"
            )
        return current_user

    return role_checker


# Convenient role dependency shortcuts
require_admin = require_roles(UserRole.ADMIN)
require_csm_or_admin = require_roles(UserRole.ADMIN, UserRole.CUSTOMER_SUCCESS_MANAGER)
require_any_authenticated = require_roles(
    UserRole.ADMIN, UserRole.CUSTOMER_SUCCESS_MANAGER, UserRole.VIEWER
)

