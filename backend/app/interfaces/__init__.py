"""Interfaces Package.

Exports all structural protocols and interfaces for repositories, services,
AI providers, and caching mechanisms.
"""

from app.interfaces.repository import (
    IBaseRepository,
    ICustomerRepository,
    IInteractionRepository,
    IInsightRepository,
    IUserRepository,
)
from app.interfaces.service import (
    ICustomerService,
    IInteractionService,
    IAIService,
    IDashboardService,
    IAuthService,
)
from app.interfaces.ai_provider import IAIProvider
from app.interfaces.cache_service import ICacheService

__all__ = [
    "IBaseRepository",
    "ICustomerRepository",
    "IInteractionRepository",
    "IInsightRepository",
    "IUserRepository",
    "ICustomerService",
    "IInteractionService",
    "IAIService",
    "IDashboardService",
    "IAuthService",
    "IAIProvider",
    "ICacheService",
]

