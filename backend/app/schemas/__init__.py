"""Schemas Package.

Central export module for all Pydantic request and response schemas, filters, and models.
"""

from app.schemas.common import APIResponse, ErrorResponse, PaginatedData
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    AuthUserSummary,
    RefreshTokenRequest,
)
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
)
from app.schemas.customer import (
    CustomerBase,
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerFilterParams,
)
from app.schemas.interaction import (
    InteractionCreate,
    InteractionUpdate,
    InteractionResponse,
    InteractionFilterParams,
)
from app.schemas.insight import (
    AIInsightSchema,
    AIInsightResponse,
    AIInsightGenerateRequest,
)
from app.schemas.dashboard import (
    DashboardSummaryResponse,
    SentimentDistribution,
    HealthDistribution,
    StatusDistribution,
    RiskSummary,
    ActionItemSummary,
    SentimentDistributionSchema,
    HealthDistributionSchema,
    StatusDistributionSchema,
    RiskSummarySchema,
    ActionItemSummarySchema,
)

__all__ = [
    "APIResponse",
    "ErrorResponse",
    "PaginatedData",
    "LoginRequest",
    "RegisterRequest",
    "TokenResponse",
    "AuthUserSummary",
    "RefreshTokenRequest",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "CustomerBase",
    "CustomerCreate",
    "CustomerUpdate",
    "CustomerResponse",
    "CustomerFilterParams",
    "InteractionCreate",
    "InteractionUpdate",
    "InteractionResponse",
    "InteractionFilterParams",
    "AIInsightSchema",
    "AIInsightResponse",
    "AIInsightGenerateRequest",
    "DashboardSummaryResponse",
    "SentimentDistribution",
    "HealthDistribution",
    "StatusDistribution",
    "RiskSummary",
    "ActionItemSummary",
    "SentimentDistributionSchema",
    "HealthDistributionSchema",
    "StatusDistributionSchema",
    "RiskSummarySchema",
    "ActionItemSummarySchema",
]

