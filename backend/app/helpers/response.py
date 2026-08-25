"""Standard API Response Envelope Builders.

Provides convenience helper functions to assemble uniform JSON envelope responses for
single records, paginated collections, and error payloads.
"""

from typing import Any, Generic, List, Optional, TypeVar
from app.schemas.common import APIResponse, ErrorResponse
from app.utils.pagination import PaginatedData, create_paginated_response

T = TypeVar("T")


def api_response(
    data: Optional[T] = None,
    message: str = "Operation completed successfully",
    success: bool = True,
    errors: Optional[Any] = None,
) -> APIResponse[T]:
    """Helper to construct standardized APIResponse models.

    Args:
        data: Optional payload data structure.
        message: Human-readable status message.
        success: Boolean flag indicating success.
        errors: Optional error details.

    Returns:
        APIResponse[T]: Generic response model envelope.
    """
    return APIResponse[T](
        success=success,
        data=data,
        message=message,
        errors=errors,
    )


def paginated_api_response(
    items: List[T],
    total: int,
    page: int,
    page_size: int,
    message: str = "Items retrieved successfully",
) -> APIResponse[PaginatedData[T]]:
    """Helper to construct standardized paginated API responses.

    Args:
        items: List of data items for the current page.
        total: Total record count across all pages.
        page: Current 1-based page index.
        page_size: Maximum items per page.
        message: Human-readable status message.

    Returns:
        APIResponse[PaginatedData[T]]: Paginated response envelope.
    """
    paginated_data = create_paginated_response(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )
    return APIResponse[PaginatedData[T]](
        success=True,
        data=paginated_data,
        message=message,
    )


def error_api_response(
    message: str = "An error occurred",
    errors: Optional[Any] = None,
) -> ErrorResponse:
    """Helper to construct standardized ErrorResponse models.

    Args:
        message: Explanation of error.
        errors: Detailed validation errors or error objects.

    Returns:
        ErrorResponse: Error envelope.
    """
    return ErrorResponse(
        success=False,
        data=None,
        message=message,
        errors=errors,
    )

