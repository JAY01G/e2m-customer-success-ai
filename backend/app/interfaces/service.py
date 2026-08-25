"""Service Layer Interface Protocols.

Defines structural typing interfaces for domain service layers including
Customer management, Interaction orchestration, AI insight generation,
Executive dashboard aggregations, and User authentication.
"""

import uuid
from typing import Any, Optional, Protocol


class ICustomerService(Protocol):
    """Customer domain service interface."""

    def get_by_id(self, customer_id: uuid.UUID) -> Any:
        """Fetch a customer by UUID or raise NotFoundException."""
        ...

    def get_all_paginated(
        self, filters: Any, page: int = 1, page_size: int = 10
    ) -> Any:
        """Fetch paginated customer response envelope with applied filters."""
        ...

    def create(self, data: Any, current_user_id: Optional[uuid.UUID] = None) -> Any:
        """Validate and create a new customer entity."""
        ...

    def update(self, customer_id: uuid.UUID, data: Any) -> Any:
        """Update customer fields and re-evaluate health thresholds."""
        ...

    def delete(self, customer_id: uuid.UUID) -> None:
        """Delete a customer and invalidate associated caches."""
        ...


class IInteractionService(Protocol):
    """Interaction domain service interface."""

    def get_by_id(self, interaction_id: uuid.UUID) -> Any:
        """Fetch an interaction by UUID or raise NotFoundException."""
        ...

    def get_all_paginated(
        self, filters: Any, page: int = 1, page_size: int = 10
    ) -> Any:
        """Fetch paginated interaction list with applied query filters."""
        ...

    async def create(
        self, data: Any, current_user_id: Optional[uuid.UUID] = None
    ) -> Any:
        """Log a new interaction and optionally trigger AI analysis pipeline."""
        ...

    def update(self, interaction_id: uuid.UUID, data: Any) -> Any:
        """Update interaction details."""
        ...

    def delete(self, interaction_id: uuid.UUID) -> None:
        """Delete an interaction record."""
        ...


class IAIService(Protocol):
    """AI intelligence and LLM orchestration service interface."""

    async def generate_and_save_insight(
        self, interaction: Any, regenerate: bool = False
    ) -> Any:
        """Invoke AI provider to extract structured insights and persist to database."""
        ...


class IDashboardService(Protocol):
    """Dashboard metrics aggregation service interface."""

    def get_summary(self) -> Any:
        """Compute and return full dashboard analytics with caching support."""
        ...


class IAuthService(Protocol):
    """Authentication and identity token service interface."""

    def register(self, data: Any) -> Any:
        """Register a new user account and return JWT credentials."""
        ...

    def login(self, data: Any) -> Any:
        """Authenticate user credentials and issue access/refresh tokens."""
        ...

    def refresh(self, refresh_token: str) -> Any:
        """Validate refresh token and issue a fresh access token."""
        ...

