"""Executive Dashboard Analytics and Aggregation Schemas.

Defines Pydantic models for executive metrics, sentiment distribution breakdowns,
health score buckets, churn-risk customer highlights, and action item queues.
"""

import uuid
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict
from app.models.customer import CustomerStatus
from app.models.ai_insight import SentimentType
from app.schemas.customer import CustomerResponse
from app.schemas.interaction import InteractionResponse


class SentimentDistribution(BaseModel):
    """Aggregate distribution counts and percentages of customer sentiment across interactions."""

    positive: int = 0
    neutral: int = 0
    negative: int = 0
    positive_percentage: float = 0.0
    neutral_percentage: float = 0.0
    negative_percentage: float = 0.0


class HealthDistribution(BaseModel):
    """Customer account breakdown by health score tiers (healthy, moderate, critical)."""

    healthy: int = 0      # 80-100
    moderate: int = 0     # 50-79
    critical: int = 0     # 0-49


class StatusDistribution(BaseModel):
    """Customer account breakdown by lifecycle status."""

    active: int = 0
    at_risk: int = 0
    churned: int = 0
    prospect: int = 0


class ActionItemSummary(BaseModel):
    """Actionable follow-up item derived from customer interaction transcripts."""

    interaction_id: uuid.UUID
    customer_name: str
    company_name: str
    action_item: str


class RiskSummary(BaseModel):
    """Flagged customer risk, churn indicator, or blocker with sentiment metadata."""

    interaction_id: uuid.UUID
    customer_name: str
    company_name: str
    risk: str
    sentiment: SentimentType


class DashboardSummaryResponse(BaseModel):
    """Aggregated executive dashboard data payload."""

    total_customers: int
    active_customers: int
    at_risk_customers: int
    churned_customers: int
    prospect_customers: int
    average_health_score: float
    total_interactions: int
    recent_interactions_count: int
    sentiment_distribution: SentimentDistribution
    health_distribution: HealthDistribution
    status_distribution: StatusDistribution
    recent_interactions: List[InteractionResponse]
    at_risk_customers_list: List[CustomerResponse]
    recent_risks: List[RiskSummary]
    recent_action_items: List[ActionItemSummary]


# Schemas Aliases
SentimentDistributionSchema = SentimentDistribution
HealthDistributionSchema = HealthDistribution
StatusDistributionSchema = StatusDistribution
RiskSummarySchema = RiskSummary
ActionItemSummarySchema = ActionItemSummary

