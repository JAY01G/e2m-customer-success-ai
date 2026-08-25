"""Interaction HTTP Controller.

Handles HTTP requests for customer touchpoint logging, listing, detail views,
updates, and deletions.
"""

import uuid
from sqlalchemy.orm import Session
from app.helpers import api_response
from app.models.user import User
from app.schemas import (
    APIResponse,
    InteractionCreate,
    InteractionFilterParams,
    InteractionResponse,
    InteractionUpdate,
    PaginatedData,
)
from app.services.interaction_service import InteractionService


class InteractionController:
    """Controller handling Interaction logging and query filtering endpoints."""

    @staticmethod
    def get_interactions(
        filters: InteractionFilterParams,
        page: int,
        page_size: int,
        db: Session,
    ) -> APIResponse[PaginatedData[InteractionResponse]]:
        """Retrieve paginated and filtered list of interactions.

        Args:
            filters: Filter and sort parameter schema.
            page: 1-based page index.
            page_size: Maximum items per page.
            db: Database session.

        Returns:
            APIResponse[PaginatedData[InteractionResponse]]: Paginated interaction response envelope.
        """
        service = InteractionService(db)
        data = service.get_all_paginated(filters=filters, page=page, page_size=page_size)
        return api_response(
            data=data,
            message="Interactions retrieved successfully",
        )

    @staticmethod
    def get_interaction(interaction_id: uuid.UUID, db: Session) -> APIResponse[InteractionResponse]:
        """Retrieve single interaction details with AI insights by UUID.

        Args:
            interaction_id: Interaction UUID.
            db: Database session.

        Returns:
            APIResponse[InteractionResponse]: Interaction detail envelope.
        """
        service = InteractionService(db)
        interaction = service.get_by_id(interaction_id)
        return api_response(
            data=InteractionResponse.model_validate(interaction),
            message="Interaction retrieved successfully",
        )

    @staticmethod
    async def create_interaction(
        current_user: User, req: InteractionCreate, db: Session
    ) -> APIResponse[InteractionResponse]:
        """Record a new interaction and execute background AI insight generation.

        Args:
            current_user: Authenticated creator user.
            req: Interaction creation payload.
            db: Database session.

        Returns:
            APIResponse[InteractionResponse]: Created interaction with AI insights.
        """
        service = InteractionService(db)
        interaction = await service.create(user_id=current_user.id, data=req)
        return api_response(
            data=InteractionResponse.model_validate(interaction),
            message="Interaction recorded and AI analysis processed successfully",
        )

    @staticmethod
    def update_interaction(
        interaction_id: uuid.UUID, req: InteractionUpdate, db: Session
    ) -> APIResponse[InteractionResponse]:
        """Update an existing interaction record.

        Args:
            interaction_id: Interaction UUID.
            req: Interaction update fields.
            db: Database session.

        Returns:
            APIResponse[InteractionResponse]: Updated interaction envelope.
        """
        service = InteractionService(db)
        interaction = service.update(interaction_id, req)
        return api_response(
            data=InteractionResponse.model_validate(interaction),
            message="Interaction updated successfully",
        )

    @staticmethod
    def delete_interaction(interaction_id: uuid.UUID, db: Session) -> APIResponse[None]:
        """Delete an interaction record.

        Args:
            interaction_id: Interaction UUID.
            db: Database session.

        Returns:
            APIResponse[None]: Deletion confirmation envelope.
        """
        service = InteractionService(db)
        service.delete(interaction_id)
        return api_response(
            data=None,
            message="Interaction deleted successfully",
        )

