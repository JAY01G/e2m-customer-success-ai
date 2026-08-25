"""User Request and Response Schemas.

Defines Pydantic models for user profile creation, updates, role modifications,
and serializable API response representations with field validators.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from app.models.user import UserRole
from app.schemas.auth import validate_password_complexity


class UserBase(BaseModel):
    """Base schema containing shared user attributes."""

    name: str = Field(..., min_length=2, max_length=100, description="User Full Name")
    email: EmailStr = Field(..., description="User Email Address")
    role: UserRole = Field(default=UserRole.CUSTOMER_SUCCESS_MANAGER, description="RBAC Role")
    is_active: bool = Field(default=True, description="Account active status")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate that name is not whitespace only."""
        trimmed = v.strip()
        if len(trimmed) < 2:
            raise ValueError("Name must be at least 2 characters long and cannot be whitespace only")
        return trimmed

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: EmailStr) -> str:
        """Normalize email address to lowercase."""
        return str(v).strip().lower()


class UserCreate(UserBase):
    """Schema for creating a new user with password."""

    password: str = Field(..., min_length=8, max_length=128, description="Initial Password")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Enforce password complexity rules."""
        return validate_password_complexity(v)


class UserUpdate(BaseModel):
    """Schema for updating editable user profile fields."""

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8, max_length=128)

    @field_validator("name")
    @classmethod
    def validate_name_update(cls, v: Optional[str]) -> Optional[str]:
        """Validate name when provided on update."""
        if v is None:
            return None
        trimmed = v.strip()
        if len(trimmed) < 2:
            raise ValueError("Name must be at least 2 characters long and cannot be whitespace only")
        return trimmed

    @field_validator("email")
    @classmethod
    def normalize_email_update(cls, v: Optional[EmailStr]) -> Optional[str]:
        """Normalize email address to lowercase."""
        if v is None:
            return None
        return str(v).strip().lower()

    @field_validator("password")
    @classmethod
    def validate_password_update(cls, v: Optional[str]) -> Optional[str]:
        """Enforce password complexity rules when password is updated."""
        if v is None:
            return None
        return validate_password_complexity(v)


class UserRoleUpdate(BaseModel):
    """Schema for administrative role assignment."""

    role: UserRole


class UserResponse(BaseModel):
    """Schema for user representation returned by API endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
