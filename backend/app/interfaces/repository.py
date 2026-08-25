"""Repository Protocol and Interface Contracts.

Defines decoupled structural typing protocols for data persistence access across
Users, Customers, Interactions, and AI Insights.
"""

import uuid
from typing import Any, Generic, List, Optional, Protocol, Tuple, TypeVar

T = TypeVar("T")


class IBaseRepository(Protocol, Generic[T]):
    """Generic repository protocol defining standard CRUD operations."""

    def get_by_id(self, entity_id: uuid.UUID) -> Optional[T]:
        """Retrieve entity by its unique UUID identifier."""
        ...

    def get_all(self) -> List[T]:
        """Retrieve all entity instances."""
        ...

    def create(self, entity: T) -> T:
        """Persist a new entity instance."""
        ...

    def update(self, entity: T) -> T:
        """Update and commit an existing entity instance."""
        ...

    def delete(self, entity: T) -> None:
        """Delete an entity instance from storage."""
        ...


class ICustomerRepository(Protocol):
    """Customer data repository interface."""

    def get_by_id(self, customer_id: uuid.UUID) -> Optional[Any]:
        """Retrieve customer record with eager loaded owner by UUID."""
        ...

    def get_by_email(self, email: str) -> Optional[Any]:
        """Retrieve customer record matching email address."""
        ...

    def get_all_paginated(
        self,
        search: Optional[str] = None,
        status: Optional[Any] = None,
        owner_id: Optional[uuid.UUID] = None,
        min_health_score: Optional[int] = None,
        max_health_score: Optional[int] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[List[Any], int]:
        """Retrieve paginated, filtered, and sorted customer records."""
        ...


class IInteractionRepository(Protocol):
    """Interaction data repository interface."""

    def get_by_id(self, interaction_id: uuid.UUID) -> Optional[Any]:
        """Retrieve interaction record with nested relationships by UUID."""
        ...

    def get_all_paginated(
        self,
        customer_id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None,
        interaction_type: Optional[Any] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[List[Any], int]:
        """Retrieve paginated and filtered interaction records."""
        ...


class IInsightRepository(Protocol):
    """AI insight data repository interface."""

    def get_by_interaction_id(self, interaction_id: uuid.UUID) -> Optional[Any]:
        """Retrieve AI insight record linked to a specific interaction UUID."""
        ...

    def create_or_update(self, insight: Any) -> Any:
        """Create or update insight entity in storage."""
        ...


class IUserRepository(Protocol):
    """User and authentication data repository interface."""

    def get_by_id(self, user_id: uuid.UUID) -> Optional[Any]:
        """Retrieve user record by unique UUID."""
        ...

    def get_by_email(self, email: str) -> Optional[Any]:
        """Retrieve user record matching normalized email."""
        ...

