"""Customer Request, Response, and Query Filter Schemas.

Defines Pydantic models for customer account creation, updates, serialized
responses (including nested owner profiles), and query filter parameters with robust validation.
"""

import re
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator
from app.models.customer import CustomerStatus
from app.schemas.user import UserResponse

PHONE_CHARS_REGEX = re.compile(r"^\+?[0-9\s\-().]{7,25}$")
ALLOWED_SORT_FIELDS = {"created_at", "updated_at", "health_score", "name", "company_name", "status"}


def validate_phone_number_format(v: Optional[str]) -> Optional[str]:
    """Validate phone number string for standard international/local format."""
    if v is None:
        return None
    trimmed = v.strip()
    if not trimmed:
        return None
    digit_count = sum(1 for c in trimmed if c.isdigit())
    if digit_count < 7 or not PHONE_CHARS_REGEX.match(trimmed):
        raise ValueError(
            "Invalid phone number format. Please provide a valid international or local number (e.g., +1 555-123-4567)"
        )
    return trimmed


class CustomerBase(BaseModel):
    """Base schema containing common customer account attributes."""

    name: str = Field(..., min_length=1, max_length=150, description="Primary Contact Name")
    company_name: str = Field(..., min_length=1, max_length=150, description="Company/Account Name")
    email: EmailStr = Field(..., description="Customer Primary Email")
    phone: Optional[str] = Field(None, max_length=50, description="Customer Phone Number")
    industry: Optional[str] = Field(None, max_length=100, description="Industry Vertical")
    status: CustomerStatus = Field(default=CustomerStatus.ACTIVE, description="Account Lifecycle Status")
    health_score: int = Field(default=100, ge=0, le=100, description="Customer Health Score (0-100)")
    owner_id: Optional[uuid.UUID] = Field(None, description="Assigned User / CSM UUID")
    notes: Optional[str] = Field(None, max_length=5000, description="Account Notes and Objectives")

    @field_validator("name", "company_name")
    @classmethod
    def validate_non_blank_strings(cls, v: str) -> str:
        """Ensure name and company name are not empty or blank whitespace."""
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Field cannot be empty or whitespace only")
        return trimmed

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format if provided."""
        return validate_phone_number_format(v)

    @field_validator("industry")
    @classmethod
    def validate_industry(cls, v: Optional[str]) -> Optional[str]:
        """Trim industry string."""
        if v is None:
            return None
        trimmed = v.strip()
        return trimmed if trimmed else None

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: Optional[str]) -> Optional[str]:
        """Trim notes string."""
        if v is None:
            return None
        trimmed = v.strip()
        return trimmed if trimmed else None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: EmailStr) -> str:
        """Normalize email address to lowercase."""
        return str(v).strip().lower()


class CustomerCreate(CustomerBase):
    """Schema for creating a new customer account record."""

    pass


class CustomerUpdate(BaseModel):
    """Schema for updating an existing customer account."""

    name: Optional[str] = Field(None, min_length=1, max_length=150)
    company_name: Optional[str] = Field(None, min_length=1, max_length=150)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    industry: Optional[str] = Field(None, max_length=100)
    status: Optional[CustomerStatus] = None
    health_score: Optional[int] = Field(None, ge=0, le=100)
    owner_id: Optional[uuid.UUID] = None
    notes: Optional[str] = Field(None, max_length=5000)

    @field_validator("name", "company_name")
    @classmethod
    def validate_non_blank(cls, v: Optional[str]) -> Optional[str]:
        """Validate non-blank for optional string fields when provided."""
        if v is None:
            return None
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Field cannot be empty or whitespace only")
        return trimmed

    @field_validator("phone")
    @classmethod
    def validate_phone_update(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number on update."""
        return validate_phone_number_format(v)

    @field_validator("industry", "notes")
    @classmethod
    def trim_optional_strings(cls, v: Optional[str]) -> Optional[str]:
        """Trim optional string values."""
        if v is None:
            return None
        trimmed = v.strip()
        return trimmed if trimmed else None

    @field_validator("email")
    @classmethod
    def normalize_email_update(cls, v: Optional[EmailStr]) -> Optional[str]:
        """Normalize email address to lowercase."""
        if v is None:
            return None
        return str(v).strip().lower()


class CustomerResponse(BaseModel):
    """Schema for customer account representation returned in API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    company_name: str
    email: str
    phone: Optional[str] = None
    industry: Optional[str] = None
    status: CustomerStatus
    health_score: int
    owner_id: Optional[uuid.UUID] = None
    owner: Optional[UserResponse] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class CustomerFilterParams(BaseModel):
    """Query parameter schema for filtering, searching, and sorting customers."""

    search: Optional[str] = Field(None, max_length=200, description="Search across name, company_name, email")
    status: Optional[CustomerStatus] = Field(None, description="Filter by status")
    owner_id: Optional[uuid.UUID] = Field(None, description="Filter by assigned owner")
    min_health_score: Optional[int] = Field(None, ge=0, le=100)
    max_health_score: Optional[int] = Field(None, ge=0, le=100)
    sort_by: str = Field(default="created_at", description="Field to sort by: created_at, health_score, name, company_name")
    sort_order: str = Field(default="desc", description="Sort order: asc or desc")

    @field_validator("search")
    @classmethod
    def trim_search(cls, v: Optional[str]) -> Optional[str]:
        """Trim search string."""
        if v is None:
            return None
        trimmed = v.strip()
        return trimmed if trimmed else None

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v: str) -> str:
        """Validate sort field against allowed whitelist."""
        clean = v.strip().lower()
        if clean not in ALLOWED_SORT_FIELDS:
            raise ValueError(f"Invalid sort_by field '{v}'. Allowed: {', '.join(sorted(ALLOWED_SORT_FIELDS))}")
        return clean

    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v: str) -> str:
        """Validate sort order."""
        clean = v.strip().lower()
        if clean not in ("asc", "desc"):
            raise ValueError("sort_order must be either 'asc' or 'desc'")
        return clean

    @model_validator(mode="after")
    def validate_health_score_range(self) -> "CustomerFilterParams":
        """Ensure min_health_score is not greater than max_health_score."""
        if (
            self.min_health_score is not None
            and self.max_health_score is not None
            and self.min_health_score > self.max_health_score
        ):
            raise ValueError(
                f"min_health_score ({self.min_health_score}) cannot be greater than max_health_score ({self.max_health_score})"
            )
        return self
