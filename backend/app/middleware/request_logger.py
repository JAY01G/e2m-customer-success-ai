"""HTTP Request and Response Telemetry Logging Middleware.

Intercepts all HTTP transactions in the FastAPI application pipeline, capturing
correlation IDs, client metadata, latency timing, status codes, and slow-query warnings.
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.config.logging import logger


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """Middleware that intercepts requests, logs telemetry, and injects correlation headers."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process incoming HTTP request, measure response time, and record telemetry.

        Args:
            request: The incoming FastAPI HTTP request.
            call_next: The next middleware / route handler in the pipeline.

        Returns:
            Response: The HTTP response with correlation ID and latency headers.
        """
        # Assign or propagate correlation request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        client_host = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        query = str(request.url.query) if request.url.query else ""
        full_path = f"{path}?{query}" if query else path

        # Skip high-frequency health checks from verbose logging if desired
        is_health_check = path in ("/health", "/ready")

        if not is_health_check:
            logger.info(f"--> [REQ:{request_id[:8]}] {method} {full_path} (Client: {client_host})")

        start_time = time.perf_counter()
        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000.0

            # Inject diagnostic headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"

            status_code = response.status_code

            if not is_health_check:
                log_msg = f"<-- [REQ:{request_id[:8]}] {method} {path} - {status_code} ({duration_ms:.1f}ms)"
                if status_code >= 500:
                    logger.error(log_msg)
                elif status_code >= 400:
                    logger.warning(log_msg)
                else:
                    logger.info(log_msg)

                # Slow response alert
                if duration_ms > 1000:
                    logger.warning(f"SLOW ENDPOINT ALERT: {method} {path} took {duration_ms:.2f}ms (>1000ms threshold)")

            return response

        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(
                f"<-- [REQ:{request_id[:8]}] {method} {path} - FAILED ({duration_ms:.1f}ms): {exc}",
                exc_info=True,
            )
            raise exc
