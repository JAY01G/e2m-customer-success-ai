"""AI Insights API Router.

Mounts endpoints for on-demand generation/regeneration of LLM intelligence
from customer interaction notes and insight retrieval.
"""

import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.controllers.insight_controller import InsightController
from app.database.dependencies import get_db
from app.dependencies.permissions import (
    require_any_authenticated,
    require_csm_or_admin,
)
from app.models.user import User
from app.schemas import APIResponse, AIInsightResponse
from app.schemas.insight import AIInsightGenerateRequest

router = APIRouter(tags=["AI Insights"])


@router.post(
    "/interactions/{interaction_id}/insights",
    response_model=APIResponse[AIInsightResponse],
    status_code=status.HTTP_200_OK,
    summary="Generate or regenerate AI insight for interaction notes (CSM and Admin)",
    response_description="Generated AI intelligence insight including sentiment, action items, and risks",
)
async def generate_insight(
    interaction_id: uuid.UUID,
    req: AIInsightGenerateRequest = AIInsightGenerateRequest(regenerate=False),
    current_user: User = Depends(require_csm_or_admin),
    db: Session = Depends(get_db),
):
    """Trigger AI LLM extraction for an interaction, producing summary, sentiment, action items, and risks.

    Args:
        interaction_id: Target interaction UUID.
        req: Generation options (e.g. force regenerate).
        current_user: Authenticated CSM or Admin user.
        db: Scoped database session.

    Returns:
        APIResponse[AIInsightResponse]: Insight response envelope.
    """
    return await InsightController.generate_insight(
        interaction_id=interaction_id, req=req, db=db
    )


@router.get(
    "/interactions/{interaction_id}/insights",
    response_model=APIResponse[AIInsightResponse],
    status_code=status.HTTP_200_OK,
    summary="Get existing AI insight for interaction",
    response_description="Persisted AI intelligence insight for the specified interaction",
)
def get_insight(
    interaction_id: uuid.UUID,
    current_user: User = Depends(require_any_authenticated),
    db: Session = Depends(get_db),
):
    """Retrieve existing AI insight for an interaction.

    Args:
        interaction_id: Target interaction UUID.
        current_user: Authenticated operator.
        db: Scoped database session.

    Returns:
        APIResponse[AIInsightResponse]: Insight response envelope.
    """
    return InsightController.get_insight(
        interaction_id=interaction_id, db=db
    )


