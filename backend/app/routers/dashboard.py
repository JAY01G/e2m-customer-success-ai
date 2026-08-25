"""Executive Dashboard API Router.

Mounts endpoints for executive KPIs, health distributions, sentiment analytics,
and urgent at-risk account queues.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.controllers.dashboard_controller import DashboardController
from app.database.dependencies import get_db
from app.dependencies.permissions import require_any_authenticated
from app.models.user import User
from app.schemas import APIResponse, DashboardSummaryResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=APIResponse[DashboardSummaryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get aggregated Customer Success metrics, distributions, recent risks, and action items",
    response_description="Consolidated executive metrics, health score distribution, and AI sentiment breakdown",
)

def get_dashboard_summary(
    current_user: User = Depends(require_any_authenticated),
    db: Session = Depends(get_db),
):
    """Retrieve summarized executive dashboard data with Redis caching.

    Args:
        current_user: Authenticated operator user.
        db: Scoped database session.

    Returns:
        APIResponse[DashboardSummaryResponse]: Consolidated dashboard metrics envelope.
    """
    return DashboardController.get_summary(db=db)

