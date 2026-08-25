"""AI-Generated Insights and Meeting Analysis ORM Models.

Defines the AIInsight entity storing LLM-derived meeting summaries, sentiment
classification (Positive, Neutral, Negative), action items, and risk indicators.
"""

import enum
import uuid
from typing import Any, List, Optional, TYPE_CHECKING
from sqlalchemy import Enum, ForeignKey, JSON, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.interaction import Interaction


class SentimentType(str, enum.Enum):
    """Enumeration of detected customer sentiment categories."""

    Positive = "Positive"
    Neutral = "Neutral"
    Negative = "Negative"


class GenerationStatus(str, enum.Enum):
    """Enumeration of AI generation processing states."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    FALLBACK = "FALLBACK"


class AIInsight(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """AI Insight database model representing structured analysis of interactions.

    Attributes:
        id: Unique UUID identifier.
        interaction_id: Foreign key referencing the analysed Interaction.
        summary: Executive summary of the interaction.
        sentiment: Sentiment classification (Positive, Neutral, Negative).
        action_items: JSON array of actionable follow-up items.
        risks: JSON array of flagged customer risks, blockers, or churn threats.
        model: Identifier of the AI model used to generate the insight.
        generation_status: Status of the insight generation pipeline.
        interaction: Parent Interaction relationship instance.
        created_at: UTC timestamp of record creation.
        updated_at: UTC timestamp of last record update.
    """

    __tablename__ = "ai_insights"

    interaction_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("interactions.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    sentiment: Mapped[SentimentType] = mapped_column(
        Enum(SentimentType, name="sentiment_type", create_type=False),
        default=SentimentType.Neutral,
        nullable=False,
    )
    action_items: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    risks: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    model: Mapped[str] = mapped_column(String(100), default="gpt-4o-mini", nullable=False)
    generation_status: Mapped[GenerationStatus] = mapped_column(
        Enum(GenerationStatus, name="generation_status", create_type=False),
        default=GenerationStatus.SUCCESS,
        nullable=False,
    )

    # Relationships
    interaction: Mapped["Interaction"] = relationship("Interaction", back_populates="ai_insight")

    def __repr__(self) -> str:
        """Return developer-friendly string representation of the AIInsight instance."""
        return f"<AIInsight id={self.id} sentiment={self.sentiment} status={self.generation_status}>"

