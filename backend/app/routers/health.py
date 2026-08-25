"""Health and Readiness Probes API Router.

Provides standard liveness and dependency readiness probe endpoints for orchestrators.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database.dependencies import get_db
from app.services.cache_service import cache_service

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Liveness health check",
    response_description="Application liveness confirmation status",
)
def health_check():
    """Liveness probe verifying that the FastAPI application process is running.

    Returns:
        dict: Process status dictionary.
    """
    return {"status": "ok", "message": "Service is live"}


@router.get(
    "/ready",
    summary="Readiness health check for PostgreSQL and Redis",
    response_description="Dependency connection statuses and service readiness code",
)
def readiness_check(db: Session = Depends(get_db)):
    """Readiness probe checking active PostgreSQL and Redis connections.

    Args:
        db: Scoped database session.

    Returns:
        JSONResponse: 200 OK if critical dependencies are healthy, 503 otherwise.
    """
    db_healthy = False
    redis_healthy = False

    # Check Database connection
    try:
        db.execute(text("SELECT 1"))
        db_healthy = True
    except Exception:
        db_healthy = False

    # Check Redis
    redis_healthy = cache_service.is_healthy()

    is_ready = db_healthy  # DB is critical, Redis is non-critical for basic operation

    status_code = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if is_ready else "not_ready",
            "database": "connected" if db_healthy else "unavailable",
            "redis": "connected" if redis_healthy else "unavailable",
        },
    )


