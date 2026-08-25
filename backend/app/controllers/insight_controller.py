"""AI Insight HTTP Controller.

Handles HTTP requests for on-demand AI insight generation and single insight retrieval.
"""

import uuid
from sqlalchemy.orm import Session
from app.exceptions.custom_exceptions import NotFoundException
from app.helpers import api_response
from app.repositories.interaction_repository import InteractionRepository
from app.schemas import APIResponse, AIInsightResponse
from app.schemas.insight import AIInsightGenerateRequest
from app.services.ai_service import AIService


class InsightController:
    """Controller handling AI insight extraction and query endpoints."""

    @staticmethod
    async def generate_insight(
        interaction_id: uuid.UUID,
        req: AIInsightGenerateRequest,
        db: Session,
    ) -> APIResponse[AIInsightResponse]:
        """Trigger AI analysis for an interaction and return structured insight envelope.

        Args:
            interaction_id: Target interaction UUID.
            req: Re-analysis configuration options.
            db: Database session.

        Returns:
            APIResponse[AIInsightResponse]: Insight response envelope.

        Raises:
            NotFoundException: If the interaction does not exist.
        """
        interaction_repo = InteractionRepository(db)
        interaction = interaction_repo.get_by_id(interaction_id)
        if not interaction:
            raise NotFoundException(f"Interaction with ID '{interaction_id}' not found")

        ai_service = AIService(db)
        insight = await ai_service.generate_and_save_insight(
            interaction=interaction,
            regenerate=req.regenerate,
        )

        return api_response(
            data=AIInsightResponse.model_validate(insight),
            message="AI insight generated and persisted successfully",
        )

    @staticmethod
    def get_insight(
        interaction_id: uuid.UUID, db: Session
    ) -> APIResponse[AIInsightResponse]:
        """Retrieve existing AI insight for an interaction.

        Args:
            interaction_id: Interaction UUID.
            db: Database session.

        Returns:
            APIResponse[AIInsightResponse]: Insight detail envelope.

        Raises:
            NotFoundException: If no insight exists for the given interaction.
        """
        ai_service = AIService(db)
        insight = ai_service.insight_repo.get_by_interaction_id(interaction_id)
        if not insight:
            raise NotFoundException(f"No AI insight found for interaction ID '{interaction_id}'")

        return api_response(
            data=AIInsightResponse.model_validate(insight),
            message="AI insight retrieved successfully",
        )

