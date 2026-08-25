"""Customer Entity ORM Models.

Defines the Customer entity representing client accounts, including health score metrics,
lifecycle statuses (ACTIVE, AT_RISK, CHURNED, PROSPECT), and assigned CSM account owners.
"""

import enum
import uuid
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import CheckConstraint, Enum, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.interaction import Interaction


class CustomerStatus(str, enum.Enum):
    """Enumeration of customer account lifecycle states."""

    ACTIVE = "ACTIVE"
    AT_RISK = "AT_RISK"
    CHURNED = "CHURNED"
    PROSPECT = "PROSPECT"


class Customer(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Customer database model representing client accounts.

    Attributes:
        id: Unique UUID identifier.
        name: Primary contact person's name.
        company_name: Name of the customer organization.
        email: Primary contact email address.
        phone: Optional contact telephone number.
        industry: Business industry classification.
        status: Lifecycle status of the customer (ACTIVE, AT_RISK, CHURNED, PROSPECT).
        health_score: Composite retention/satisfaction score (0-100).
        owner_id: UUID of assigned CSM / Account Owner.
        notes: General account observations or remarks.
        owner: User relationship representing the account manager.
        interactions: List of historical interactions associated with this customer.
        created_at: UTC timestamp of record creation.
        updated_at: UTC timestamp of last record update.
    """

    __tablename__ = "customers"
    __table_args__ = (
        CheckConstraint("health_score >= 0 AND health_score <= 100", name="check_health_score_range"),
    )

    name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    company_name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[CustomerStatus] = mapped_column(
        Enum(CustomerStatus, name="customer_status", create_type=False),
        default=CustomerStatus.ACTIVE,
        index=True,
        nullable=False,
    )
    health_score: Mapped[int] = mapped_column(
        Integer, default=100, index=True, nullable=False
    )
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    owner: Mapped[Optional["User"]] = relationship("User", back_populates="customers")
    interactions: Mapped[List["Interaction"]] = relationship(
        "Interaction",
        back_populates="customer",
        cascade="all, delete-orphan",
        order_by="desc(Interaction.meeting_date)",
    )

    def __repr__(self) -> str:
        """Return developer-friendly string representation of the Customer instance."""
        return f"<Customer id={self.id} company={self.company_name} status={self.status} health={self.health_score}>"

