"""Customer Interaction and Touchpoint Orchestration Service.

Manages customer meeting logs, automated trigger of AI insight analysis pipelines,
interaction pagination, and cache invalidation.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.config.logging import logger
from app.exceptions.custom_exceptions import NotFoundException, ValidationException
from app.models.interaction import Interaction
from app.repositories.customer_repository import CustomerRepository
from app.repositories.interaction_repository import InteractionRepository
from app.schemas.interaction import (
    InteractionCreate,
    InteractionFilterParams,
    InteractionResponse,
    InteractionUpdate,
)
from app.services.ai_service import AIService
from app.services.cache_service import cache_service
from app.utils.pagination import PaginatedData, create_paginated_response


class InteractionService:
    """Service handling touchpoint logging, AI analysis triggers, updates, and cache eviction."""

    def __init__(self, db: Session):
        """Initialize InteractionService with database session, repositories, and AIService.

        Args:
            db: Scoped SQLAlchemy database session.
        """
        self.db = db
        self.interaction_repo = InteractionRepository(db)
        self.customer_repo = CustomerRepository(db)
        self.ai_service = AIService(db)

    def get_by_id(self, interaction_id: uuid.UUID) -> Interaction:
        """Fetch an interaction by UUID with joined relationships.

        Args:
            interaction_id: Unique UUID of the interaction.

        Returns:
            Interaction: Populated Interaction ORM entity.

        Raises:
            NotFoundException: If no interaction matches the given UUID.
        """
        interaction = self.interaction_repo.get_by_id(interaction_id)
        if not interaction:
            raise NotFoundException(f"Interaction with ID '{interaction_id}' not found")
        return interaction

    def get_all_paginated(
        self,
        filters: InteractionFilterParams,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedData[InteractionResponse]:
        """Retrieve paginated and filtered list of customer interactions.

        Args:
            filters: Filter and sort parameter schema.
            page: 1-based page index.
            page_size: Page size limit.

        Returns:
            PaginatedData[InteractionResponse]: Paginated interaction response envelope.
        """
        offset = (page - 1) * page_size
        items, total = self.interaction_repo.get_all_paginated(
            filters, offset=offset, limit=page_size
        )
        response_items = [InteractionResponse.model_validate(item) for item in items]
        return create_paginated_response(response_items, total, page, page_size)

    async def create(
        self, user_id: uuid.UUID, data: InteractionCreate
    ) -> Interaction:
        """Create a new interaction record and optionally trigger background AI analysis.

        Args:
            user_id: UUID of the creator/author user.
            data: Interaction creation payload.

        Returns:
            Interaction: Persisted Interaction entity with generated AI insights.

        Raises:
            NotFoundException: If referenced customer does not exist.
        """
        # Validate that customer exists
        customer = self.customer_repo.get_by_id(data.customer_id)
        if not customer:
            raise NotFoundException(f"Customer with ID '{data.customer_id}' not found")

        meeting_date = data.meeting_date or datetime.now(timezone.utc)

        new_interaction = Interaction(
            customer_id=data.customer_id,
            user_id=user_id,
            type=data.type,
            title=data.title.strip(),
            meeting_date=meeting_date,
            notes=data.notes.strip(),
            duration_minutes=data.duration_minutes or 30,
        )

        interaction = self.interaction_repo.create(new_interaction)
        logger.info(
            f"Created interaction '{interaction.title}' for customer '{customer.name}' [ID: {interaction.id}]"
        )

        # Trigger AI insight generation if requested
        if data.generate_ai_insight:
            try:
                await self.ai_service.generate_and_save_insight(interaction)
            except Exception as e:
                logger.warning(
                    f"Background AI insight generation failed for interaction {interaction.id}: {e}"
                )

        # Invalidate caches
        cache_service.invalidate_interaction_cache(str(interaction.id))
        return self.get_by_id(interaction.id)

    def update(
        self, interaction_id: uuid.UUID, data: InteractionUpdate
    ) -> Interaction:
        """Update an existing interaction record and invalidate caches.

        Args:
            interaction_id: Unique UUID of the interaction to update.
            data: Interaction update payload.

        Returns:
            Interaction: Updated Interaction entity.
        """
        interaction = self.get_by_id(interaction_id)

        if data.type is not None:
            interaction.type = data.type
        if data.title is not None:
            interaction.title = data.title.strip()
        if data.meeting_date is not None:
            interaction.meeting_date = data.meeting_date
        if data.notes is not None:
            interaction.notes = data.notes.strip()
        if data.duration_minutes is not None:
            interaction.duration_minutes = data.duration_minutes

        updated = self.interaction_repo.update(interaction)
        logger.info(f"Updated interaction [ID: {interaction_id}]")

        cache_service.invalidate_interaction_cache(str(interaction_id))
        return self.get_by_id(interaction_id)

    def delete(self, interaction_id: uuid.UUID) -> None:
        """Delete an interaction record and flush associated caches.

        Args:
            interaction_id: Unique UUID of the interaction to delete.
        """
        interaction = self.get_by_id(interaction_id)
        self.interaction_repo.delete(interaction)
        logger.info(f"Deleted interaction [ID: {interaction_id}]")

        cache_service.invalidate_interaction_cache(str(interaction_id))

