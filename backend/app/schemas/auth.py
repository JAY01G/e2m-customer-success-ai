"""Authentication Request and Response Schemas.

Defines Pydantic models for user registration, credentials login, JWT tokens,
and authenticated user identity summaries with password complexity and field validation.
"""

import re
import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.models.user import UserRole

PASSWORD_UPPERCASE = re.compile(r"[A-Z]")
PASSWORD_LOWERCASE = re.compile(r"[a-z]")
PASSWORD_DIGIT = re.compile(r"\d")
PASSWORD_SPECIAL = re.compile(r"[!@#$%^&*(),.?\":{}|<>\-_+=\[\]\\/]")


def validate_password_complexity(password: str) -> str:
    """Enforce strong password policy: length >= 8, uppercase, lowercase, digit, special character."""
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not PASSWORD_UPPERCASE.search(password):
        raise ValueError("Password must contain at least one uppercase letter (A-Z)")
    if not PASSWORD_LOWERCASE.search(password):
        raise ValueError("Password must contain at least one lowercase letter (a-z)")
    if not PASSWORD_DIGIT.search(password):
        raise ValueError("Password must contain at least one number (0-9)")
    if not PASSWORD_SPECIAL.search(password):
        raise ValueError("Password must contain at least one special character (!@#$%^&*...)")
    return password


class RegisterRequest(BaseModel):
    """Schema for user account registration payload."""

    name: str = Field(..., min_length=2, max_length=100, description="Full Name")
    email: EmailStr = Field(..., description="Valid Email Address")
    password: str = Field(
        ..., min_length=8, max_length=128, description="Strong Password (min 8 chars, mixed case, numbers, symbols)"
    )
    role: Optional[UserRole] = Field(
        default=UserRole.CUSTOMER_SUCCESS_MANAGER,
        description="Role assigned to user (Defaults to CSM)"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate that name is not empty or whitespace only."""
        trimmed = v.strip()
        if len(trimmed) < 2:
            raise ValueError("Name must be at least 2 characters long and cannot be whitespace only")
        return trimmed

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: EmailStr) -> str:
        """Normalize email address to lowercase."""
        return str(v).strip().lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Enforce password complexity rules."""
        return validate_password_complexity(v)


class LoginRequest(BaseModel):
    """Schema for user credentials login payload."""

    email: EmailStr = Field(..., description="User Email")
    password: str = Field(..., min_length=1, max_length=128, description="User Password")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: EmailStr) -> str:
        """Normalize email address to lowercase."""
        return str(v).strip().lower()


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request in JSON payload."""

    refresh_token: Optional[str] = Field(
        default=None,
        max_length=2048,
        description="Refresh token (optional if provided via HttpOnly cookie)"
    )


class AuthUserSummary(BaseModel):
    """Summarized user representation returned inside JWT authentication responses."""

    id: uuid.UUID
    name: str
    email: str
    role: UserRole
    is_active: bool


class TokenResponse(BaseModel):
    """Schema for JWT authentication response containing access and refresh tokens."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    user: AuthUserSummary


TokenResponse.model_rebuild()
