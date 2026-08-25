"""Global Exception and Error Handler Middleware.

Registers custom exception handlers with FastAPI to intercept application errors,
validation failures, database constraints, and unhandled exceptions, returning
consistent JSON API error envelopes.
"""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.config.logging import logger
from app.exceptions.custom_exceptions import AppException


def register_exception_handlers(app: FastAPI) -> None:
    """Register application-level exception handlers on the FastAPI app instance.

    Attaches handlers for `AppException`, `StarletteHTTPException`, `RequestValidationError`,
    `IntegrityError`, `SQLAlchemyError`, `KeyError`, `ValueError`, and general `Exception`
    to standardize JSON error payloads.

    Args:
        app: The FastAPI application instance to configure.
    """
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        """Handle domain-level application exceptions."""
        logger.warning(f"AppException: [{exc.status_code}] {exc.message} (Path: {request.url.path})")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "data": None,
                "message": exc.message,
                "errors": exc.errors,
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """Handle standard HTTP exceptions (e.g., 404 Not Found, 405 Method Not Allowed)."""
        logger.warning(f"HTTPException: [{exc.status_code}] {exc.detail} (Path: {request.url.path})")
        if isinstance(exc.detail, dict):
            message = exc.detail.get("message", "HTTP error occurred")
            errors = exc.detail.get("errors")
        elif isinstance(exc.detail, list):
            message = "Validation or request processing error"
            errors = exc.detail
        else:
            message = str(exc.detail) if exc.detail else "HTTP error occurred"
            errors = None

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "data": None,
                "message": message,
                "errors": errors,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle Pydantic/FastAPI request validation errors."""
        logger.warning(f"RequestValidationError: {exc.errors()} (Path: {request.url.path})")
        formatted_errors: List[Dict[str, Any]] = []
        error_summaries: List[str] = []

        for err in exc.errors():
            loc_parts = [str(l) for l in err.get("loc", []) if l not in ("body", "query", "path")]
            loc = " -> ".join(loc_parts) if loc_parts else "field"
            raw_msg = err.get("msg", "Invalid value")
            # Strip Pydantic error prefixes if present
            clean_msg = raw_msg.replace("Value error, ", "") if raw_msg.startswith("Value error, ") else raw_msg
            err_type = err.get("type", "value_error")

            formatted_errors.append({
                "field": loc,
                "message": clean_msg,
                "type": err_type,
            })
            error_summaries.append(f"{loc}: {clean_msg}")

        summary_msg = f"Validation failed: {', '.join(error_summaries[:2])}" if error_summaries else "Validation failed on request parameters"
        if len(error_summaries) > 2:
            summary_msg += f" (and {len(error_summaries) - 2} more errors)"

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "data": None,
                "message": summary_msg,
                "errors": formatted_errors,
            },
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
        """Handle relational database integrity and uniqueness violations."""
        orig_msg = str(getattr(exc, "orig", exc))
        logger.error(f"Database IntegrityError on {request.url.path}: {orig_msg}")

        detail_msg = "Database constraint violation or duplicate record"
        if "unique" in orig_msg.lower() or "duplicate" in orig_msg.lower():
            detail_msg = "A record with this information already exists"
        elif "foreign key" in orig_msg.lower():
            detail_msg = "Referenced resource does not exist or is constrained"

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "success": False,
                "data": None,
                "message": detail_msg,
                "errors": [{"detail": orig_msg}] if orig_msg else None,
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """Handle general database persistence errors."""
        logger.error(f"SQLAlchemyError on {request.url.path}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "data": None,
                "message": "A database error occurred while processing your request",
                "errors": None,
            },
        )

    @app.exception_handler(KeyError)
    async def key_error_handler(request: Request, exc: KeyError) -> JSONResponse:
        """Handle missing dictionary/request key errors as Bad Request."""
        key_name = str(exc).strip("'\"")
        logger.warning(f"KeyError on {request.url.path}: Missing key '{key_name}'")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "data": None,
                "message": f"Missing required parameter: '{key_name}'",
                "errors": [{"field": key_name, "message": f"Parameter '{key_name}' is required"}],
            },
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        """Handle ValueError as Bad Request."""
        logger.warning(f"ValueError on {request.url.path}: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "data": None,
                "message": str(exc) or "Invalid parameter value provided",
                "errors": None,
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle any unhandled server exceptions as HTTP 500 errors."""
        logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "data": None,
                "message": "An unexpected internal server error occurred",
                "errors": None,
            },
        )


