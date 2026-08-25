"""Pagination Schemas and Computation Utilities.

Defines Pydantic models for pagination parameters and generic response envelopes,
calculating SQL offsets, limits, and total page counts.
"""

import math
from typing import Generic, List, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Query parameters for offset-based pagination."""

    page: int = Field(default=1, ge=1, description="Page number starting from 1")
    page_size: int = Field(default=20, ge=1, le=100, description="Number of items per page (max 100)")

    @property
    def offset(self) -> int:
        """Calculate SQL OFFSET value."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Return SQL LIMIT value."""
        return self.page_size


class PaginatedData(BaseModel, Generic[T]):
    """Generic envelope structure containing paginated items and metadata."""

    items: List[T]
    page: int
    page_size: int
    total: int
    total_pages: int


def create_paginated_response(
    items: List[T], total: int, page: int, page_size: int
) -> PaginatedData[T]:
    """Assemble a PaginatedData object with computed total_pages.

    Args:
        items: List of items for current page.
        total: Total record count.
        page: 1-based page number.
        page_size: Maximum items per page.

    Returns:
        PaginatedData[T]: Populated paginated envelope.
    """
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    return PaginatedData(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )

