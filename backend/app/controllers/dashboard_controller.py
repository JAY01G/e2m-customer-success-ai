"""Executive Dashboard HTTP Controller.

Handles HTTP requests for retrieving summarized Customer Success KPIs and analytics.
"""

from sqlalchemy.orm import Session
from app.helpers import api_response
from app.schemas import APIResponse, DashboardSummaryResponse
from app.services.dashboard_service import DashboardService


class DashboardController:
    """Controller handling executive dashboard aggregation endpoints."""

    @staticmethod
    def get_summary(db: Session) -> APIResponse[DashboardSummaryResponse]:
        """Fetch consolidated executive dashboard analytics.

        Args:
            db: Database session.

        Returns:
            APIResponse[DashboardSummaryResponse]: Dashboard metrics and distribution envelope.
        """
        service = DashboardService(db)
        data = service.get_summary()
        return api_response(
            data=data,
            message="Dashboard summary retrieved successfully",
        )

