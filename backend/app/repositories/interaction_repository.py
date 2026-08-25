"""Interaction Data Access Repository.

Implements database queries, filtering, relationship eager-loading,
and retrieval for customer touchpoints and meetings.
"""

import uuid
from typing import List, Optional, Tuple
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload
from app.models.interaction import Interaction
from app.schemas.interaction import InteractionFilterParams


class InteractionRepository:
    """Repository managing Interaction database queries, eager-loading, and mutations."""

    def __init__(self, db: Session):
        """Initialize repository with an active SQLAlchemy database session.

        Args:
            db: Scoped database session.
        """
        self.db = db

    def get_by_id(self, interaction_id: uuid.UUID) -> Optional[Interaction]:
        """Fetch a single interaction with joined relationships (user, customer, ai_insight).

        Args:
            interaction_id: Unique UUID of the interaction.

        Returns:
            Optional[Interaction]: Fully populated Interaction ORM entity or None.
        """
        stmt = (
            select(Interaction)
            .options(
                joinedload(Interaction.user),
                joinedload(Interaction.customer),
                joinedload(Interaction.ai_insight),
            )
            .where(Interaction.id == interaction_id)
        )
        return self.db.scalars(stmt).first()

    def get_all_paginated(
        self,
        filters: InteractionFilterParams,
        offset: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Interaction], int]:
        """Retrieve paginated, filtered, and sorted interaction records.

        Args:
            filters: Filter and sort parameter schema.
            offset: Offset index for pagination.
            limit: Page size limit.

        Returns:
            Tuple[List[Interaction], int]: List of matching interaction records and total matching count.
        """
        query = select(Interaction).options(
            joinedload(Interaction.user),
            joinedload(Interaction.customer),
            joinedload(Interaction.ai_insight),
        )
        count_query = select(func.count(Interaction.id))

        if filters.customer_id:
            query = query.where(Interaction.customer_id == filters.customer_id)
            count_query = count_query.where(Interaction.customer_id == filters.customer_id)

        if filters.user_id:
            query = query.where(Interaction.user_id == filters.user_id)
            count_query = count_query.where(Interaction.user_id == filters.user_id)

        if filters.type:
            query = query.where(Interaction.type == filters.type)
            count_query = count_query.where(Interaction.type == filters.type)

        if filters.search:
            search_term = f"%{filters.search.strip()}%"
            search_clause = or_(
                Interaction.title.ilike(search_term),
                Interaction.notes.ilike(search_term),
            )
            query = query.where(search_clause)
            count_query = count_query.where(search_clause)

        if filters.start_date:
            query = query.where(Interaction.meeting_date >= filters.start_date)
            count_query = count_query.where(Interaction.meeting_date >= filters.start_date)

        if filters.end_date:
            query = query.where(Interaction.meeting_date <= filters.end_date)
            count_query = count_query.where(Interaction.meeting_date <= filters.end_date)

        total = self.db.scalar(count_query) or 0

        # Sorting
        sort_col = getattr(Interaction, filters.sort_by, Interaction.meeting_date)
        if filters.sort_order.lower() == "asc":
            query = query.order_by(sort_col.asc())
        else:
            query = query.order_by(sort_col.desc())

        query = query.offset(offset).limit(limit)
        items = list(self.db.scalars(query).all())
        return items, total

    def get_recent(self, limit: int = 5) -> List[Interaction]:
        """Fetch the most recent interactions across all customers.

        Args:
            limit: Maximum count of recent interactions.

        Returns:
            List[Interaction]: List of recent Interaction ORM entities.
        """
        stmt = (
            select(Interaction)
            .options(
                joinedload(Interaction.user),
                joinedload(Interaction.customer),
                joinedload(Interaction.ai_insight),
            )
            .order_by(Interaction.meeting_date.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def count_total(self) -> int:
        """Count the total number of logged interactions in the system.

        Returns:
            int: Total interaction count.
        """
        return self.db.scalar(select(func.count(Interaction.id))) or 0

    def create(self, interaction: Interaction) -> Interaction:
        """Persist a new interaction record.

        Args:
            interaction: Unpersisted Interaction model.

        Returns:
            Interaction: Committed and refreshed Interaction model.
        """
        self.db.add(interaction)
        self.db.commit()
        self.db.refresh(interaction)
        return interaction

    def update(self, interaction: Interaction) -> Interaction:
        """Commit updates to an existing interaction record.

        Args:
            interaction: Modified Interaction model.

        Returns:
            Interaction: Refreshed Interaction model.
        """
        self.db.commit()
        self.db.refresh(interaction)
        return interaction

    def delete(self, interaction: Interaction) -> None:
        """Delete an interaction record from storage.

        Args:
            interaction: Interaction model to delete.
        """
        self.db.delete(interaction)
        self.db.commit()

