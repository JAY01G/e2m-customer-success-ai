"""Interaction Request, Response, and Query Filter Schemas.

Defines Pydantic models for customer touchpoint logging, updates, serialized responses
with attached AI insights, and multi-field query filter parameters with robust validation.
"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from app.models.interaction import InteractionType
from app.schemas.insight import AIInsightResponse
from app.schemas.user import UserResponse

ALLOWED_INTERACTION_SORT_FIELDS = {"meeting_date", "created_at", "title", "type", "duration_minutes"}


class InteractionBase(BaseModel):
    """Base schema containing shared touchpoint attributes."""

    customer_id: uuid.UUID = Field(..., description="Target Customer UUID")
    type: InteractionType = Field(default=InteractionType.MEETING, description="Touchpoint Channel Type")
    title: str = Field(..., min_length=2, max_length=200, description="Meeting Subject / Title")
    meeting_date: Optional[datetime] = Field(None, description="Date and time when interaction took place")
    notes: str = Field(..., min_length=5, max_length=20000, description="Meeting notes or transcript summary")
    duration_minutes: Optional[int] = Field(default=30, ge=1, le=1440, description="Duration in minutes (1-1440)")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate that title is not empty or blank whitespace."""
        trimmed = v.strip()
        if len(trimmed) < 2:
            raise ValueError("Title must be at least 2 characters long and cannot be whitespace only")
        return trimmed

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: str) -> str:
        """Validate that notes are not empty or blank whitespace."""
        trimmed = v.strip()
        if len(trimmed) < 5:
            raise ValueError("Meeting notes must be at least 5 characters long and cannot be whitespace only")
        return trimmed


class InteractionCreate(InteractionBase):
    """Schema for creating a new interaction, optionally triggering automated AI analysis."""

    generate_ai_insight: bool = Field(
        default=True,
        description="Whether to automatically trigger AI insight analysis upon creation",
    )


class InteractionUpdate(BaseModel):
    """Schema for updating an existing interaction record."""

    type: Optional[InteractionType] = None
    title: Optional[str] = Field(None, min_length=2, max_length=200)
    meeting_date: Optional[datetime] = None
    notes: Optional[str] = Field(None, min_length=5, max_length=20000)
    duration_minutes: Optional[int] = Field(None, ge=1, le=1440)

    @field_validator("title")
    @classmethod
    def validate_title_update(cls, v: Optional[str]) -> Optional[str]:
        """Validate title when provided on update."""
        if v is None:
            return None
        trimmed = v.strip()
        if len(trimmed) < 2:
            raise ValueError("Title must be at least 2 characters long and cannot be whitespace only")
        return trimmed

    @field_validator("notes")
    @classmethod
    def validate_notes_update(cls, v: Optional[str]) -> Optional[str]:
        """Validate notes when provided on update."""
        if v is None:
            return None
        trimmed = v.strip()
        if len(trimmed) < 5:
            raise ValueError("Meeting notes must be at least 5 characters long and cannot be whitespace only")
        return trimmed


class InteractionResponse(BaseModel):
    """Schema for interaction representation returned in API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    customer_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    user: Optional[UserResponse] = None
    type: InteractionType
    title: str
    meeting_date: datetime
    notes: str
    duration_minutes: Optional[int] = 30
    ai_insight: Optional[AIInsightResponse] = None
    created_at: datetime
    updated_at: datetime


class InteractionFilterParams(BaseModel):
    """Query parameter schema for filtering, searching, and sorting interactions."""

    customer_id: Optional[uuid.UUID] = None
    user_id: Optional[uuid.UUID] = None
    type: Optional[InteractionType] = None
    search: Optional[str] = Field(None, max_length=200, description="Search across title and notes")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    sort_by: str = Field(default="meeting_date", description="Field to sort by")
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
        if clean not in ALLOWED_INTERACTION_SORT_FIELDS:
            raise ValueError(
                f"Invalid sort_by field '{v}'. Allowed: {', '.join(sorted(ALLOWED_INTERACTION_SORT_FIELDS))}"
            )
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
    def validate_date_range(self) -> "InteractionFilterParams":
        """Ensure start_date is not after end_date."""
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.start_date > self.end_date
        ):
            raise ValueError(
                f"start_date ({self.start_date.isoformat()}) cannot be after end_date ({self.end_date.isoformat()})"
            )
        return self
