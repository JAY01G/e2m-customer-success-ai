"""Customer Interaction and Touchpoint ORM Models.

Defines the Interaction entity representing customer touchpoints (meetings, calls,
emails, product demos) and links them to AI-generated insight summaries.
"""

import enum
import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.user import User
    from app.models.ai_insight import AIInsight


class InteractionType(str, enum.Enum):
    """Enumeration of supported interaction/touchpoint communication channels."""

    MEETING = "MEETING"
    CALL = "CALL"
    EMAIL = "EMAIL"
    DEMO = "DEMO"
    OTHER = "OTHER"


class Interaction(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Interaction database model representing customer meetings and touchpoints.

    Attributes:
        id: Unique UUID identifier.
        customer_id: Foreign key referencing the parent Customer.
        user_id: Foreign key referencing the User/CSM who conducted the interaction.
        type: Channel type (MEETING, CALL, EMAIL, DEMO, OTHER).
        title: Descriptive headline or meeting topic.
        meeting_date: Timestamp of when the interaction took place.
        notes: Raw notes, discussion transcript, or meeting minutes.
        duration_minutes: Length of the touchpoint in minutes.
        customer: Customer relationship instance.
        user: User relationship instance representing the meeting conductor.
        ai_insight: One-to-one relationship with the generated AI insight.
        created_at: UTC timestamp of record creation.
        updated_at: UTC timestamp of last record update.
    """

    __tablename__ = "interactions"

    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    type: Mapped[InteractionType] = mapped_column(
        Enum(InteractionType, name="interaction_type", create_type=False),
        default=InteractionType.MEETING,
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    meeting_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        nullable=False,
    )
    notes: Mapped[str] = mapped_column(Text, nullable=False)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, default=30, nullable=True)

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="interactions")
    user: Mapped[Optional["User"]] = relationship("User", back_populates="interactions")
    ai_insight: Mapped[Optional["AIInsight"]] = relationship(
        "AIInsight",
        back_populates="interaction",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return developer-friendly string representation of the Interaction instance."""
        return f"<Interaction id={self.id} type={self.type} title={self.title}>"

