"""Custom Application Domain Exceptions.

Provides structured, typed exceptions for common application error conditions,
including 404 Not Found, 401 Unauthorized, 403 Forbidden, 400 Bad Request,
409 Conflict, 422 Validation Error, and 503 AI Service Unavailable.
"""

from typing import Any, Dict, Optional


class AppException(Exception):
    """Base application exception with HTTP status code and optional error metadata."""

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        status_code: int = 500,
        errors: Optional[Any] = None,
    ):
        """Initialize base application exception.

        Args:
            message: Human-readable error message.
            status_code: Corresponding HTTP status code.
            errors: Optional detail/validation errors list or dictionary.
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors


class NotFoundException(AppException):
    """Exception raised when a requested resource is not found (HTTP 404)."""

    def __init__(self, message: str = "Resource not found", errors: Optional[Any] = None):
        super().__init__(message=message, status_code=404, errors=errors)


class UnauthorizedException(AppException):
    """Exception raised when authentication fails or is missing (HTTP 401)."""

    def __init__(
        self,
        message: str = "Authentication required or invalid credentials",
        errors: Optional[Any] = None,
    ):
        super().__init__(message=message, status_code=401, errors=errors)


class ForbiddenException(AppException):
    """Exception raised when an authenticated user lacks permissions (HTTP 403)."""

    def __init__(
        self,
        message: str = "You do not have permission to perform this action",
        errors: Optional[Any] = None,
    ):
        super().__init__(message=message, status_code=403, errors=errors)


class BadRequestException(AppException):
    """Exception raised when client request payload or query is invalid (HTTP 400)."""

    def __init__(self, message: str = "Bad request", errors: Optional[Any] = None):
        super().__init__(message=message, status_code=400, errors=errors)


class ConflictException(AppException):
    """Exception raised when resource state causes conflict, e.g. duplicates (HTTP 409)."""

    def __init__(
        self, message: str = "Resource already exists or conflict occurred", errors: Optional[Any] = None
    ):
        super().__init__(message=message, status_code=409, errors=errors)


class ValidationException(AppException):
    """Exception raised when business rule validation fails (HTTP 422)."""

    def __init__(self, message: str = "Validation failed", errors: Optional[Any] = None):
        super().__init__(message=message, status_code=422, errors=errors)


class AIServiceException(AppException):
    """Exception raised when external AI LLM processing fails or times out (HTTP 503)."""

    def __init__(
        self, message: str = "AI insight generation temporarily unavailable", errors: Optional[Any] = None
    ):
        super().__init__(message=message, status_code=503, errors=errors)

