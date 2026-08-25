"""Common API Response Envelopes and Schema Utilities.

Defines standardized generic success and error response wrappers (`APIResponse`, `ErrorResponse`)
for unified JSON API contracts across all endpoints.
"""

from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict
from app.utils.pagination import PaginatedData

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard generic API response envelope wrapping payload data.

    Attributes:
        success: Boolean flag indicating operation success.
        data: Generic payload data or None.
        message: Informational or success status message.
        errors: Optional list or dictionary of validation or domain error details.
    """

    model_config = ConfigDict(from_attributes=True)

    success: bool = True
    data: Optional[T] = None
    message: str = "Operation completed successfully"
    errors: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Standard API response envelope for failed requests.

    Attributes:
        success: Always False for error responses.
        data: Typically None in error states.
        message: Explanatory error message.
        errors: Detailed validation or runtime error objects.
    """

    success: bool = False
    data: Optional[Any] = None
    message: str
    errors: Optional[Any] = None


__all__ = ["APIResponse", "ErrorResponse", "PaginatedData"]

