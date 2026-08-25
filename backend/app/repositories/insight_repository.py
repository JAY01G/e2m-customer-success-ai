"""AI Insight Data Access Repository.

Implements database queries, idempotency checks (create or update),
sentiment distribution statistics, and risk/action-item extractions.
"""

import uuid
from typing import Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload
from app.models.ai_insight import AIInsight, SentimentType
from app.models.customer import Customer
from app.models.interaction import Interaction
from app.schemas.dashboard import ActionItemSummary, RiskSummary


class InsightRepository:
    """Repository managing AI Insight storage, sentiment aggregation, and risk query joins."""

    def __init__(self, db: Session):
        """Initialize repository with an active SQLAlchemy database session.

        Args:
            db: Scoped database session.
        """
        self.db = db

    def get_by_interaction_id(self, interaction_id: uuid.UUID) -> Optional[AIInsight]:
        """Retrieve AI insight associated with a specific interaction UUID.

        Args:
            interaction_id: Unique UUID of the interaction.

        Returns:
            Optional[AIInsight]: AIInsight entity if found, else None.
        """
        stmt = select(AIInsight).where(AIInsight.interaction_id == interaction_id)
        return self.db.scalars(stmt).first()

    def get_by_id(self, insight_id: uuid.UUID) -> Optional[AIInsight]:
        """Retrieve AI insight by its primary UUID.

        Args:
            insight_id: Unique UUID of the insight record.

        Returns:
            Optional[AIInsight]: AIInsight entity if found, else None.
        """
        stmt = select(AIInsight).where(AIInsight.id == insight_id)
        return self.db.scalars(stmt).first()

    def create_or_update(self, insight: AIInsight) -> AIInsight:
        """Upsert an AI insight record for an interaction to ensure idempotency.

        Args:
            insight: AIInsight entity to save.

        Returns:
            AIInsight: Persisted or updated AIInsight entity.
        """
        existing = self.get_by_interaction_id(insight.interaction_id)
        if existing:
            existing.summary = insight.summary
            existing.sentiment = insight.sentiment
            existing.action_items = insight.action_items
            existing.risks = insight.risks
            existing.model = insight.model
            existing.generation_status = insight.generation_status
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            self.db.add(insight)
            self.db.commit()
            self.db.refresh(insight)
            return insight

    def delete(self, insight: AIInsight) -> None:
        """Delete an insight record from storage.

        Args:
            insight: AIInsight entity to remove.
        """
        self.db.delete(insight)
        self.db.commit()

    def get_sentiment_distribution(self) -> Dict[str, int]:
        """Aggregate total insight counts grouped by sentiment classification.

        Returns:
            Dict[str, int]: Mapping of Positive, Neutral, Negative counts.
        """
        stmt = select(AIInsight.sentiment, func.count(AIInsight.id)).group_by(AIInsight.sentiment)
        results = self.db.execute(stmt).all()
        counts = {s.value: 0 for s in SentimentType}
        for sentiment, count in results:
            if hasattr(sentiment, "value"):
                counts[sentiment.value] = count
            else:
                counts[str(sentiment)] = count
        return counts

    def get_recent_risks(self, limit: int = 5) -> List[RiskSummary]:
        """Retrieve recently flagged risk items across all customer interactions.

        Args:
            limit: Maximum count of risk items to return.

        Returns:
            List[RiskSummary]: List of structured risk summaries with customer context.
        """
        stmt = (
            select(AIInsight, Interaction, Customer)
            .join(Interaction, AIInsight.interaction_id == Interaction.id)
            .join(Customer, Interaction.customer_id == Customer.id)
            .order_by(AIInsight.created_at.desc())
            .limit(20)
        )
        results = self.db.execute(stmt).all()
        risks_list: List[RiskSummary] = []
        for insight, interaction, customer in results:
            if insight.risks and isinstance(insight.risks, list):
                for risk_item in insight.risks:
                    risks_list.append(
                        RiskSummary(
                            interaction_id=interaction.id,
                            customer_name=customer.name,
                            company_name=customer.company_name,
                            risk=str(risk_item),
                            sentiment=insight.sentiment,
                        )
                    )
                    if len(risks_list) >= limit:
                        return risks_list
        return risks_list

    def get_recent_action_items(self, limit: int = 5) -> List[ActionItemSummary]:
        """Retrieve recently extracted action items across all customer interactions.

        Args:
            limit: Maximum count of action items to return.

        Returns:
            List[ActionItemSummary]: List of action items with customer context.
        """
        stmt = (
            select(AIInsight, Interaction, Customer)
            .join(Interaction, AIInsight.interaction_id == Interaction.id)
            .join(Customer, Interaction.customer_id == Customer.id)
            .order_by(AIInsight.created_at.desc())
            .limit(20)
        )
        results = self.db.execute(stmt).all()
        actions_list: List[ActionItemSummary] = []
        for insight, interaction, customer in results:
            if insight.action_items and isinstance(insight.action_items, list):
                for action in insight.action_items:
                    actions_list.append(
                        ActionItemSummary(
                            interaction_id=interaction.id,
                            customer_name=customer.name,
                            company_name=customer.company_name,
                            action_item=str(action),
                        )
                    )
                    if len(actions_list) >= limit:
                        return actions_list
        return actions_list

