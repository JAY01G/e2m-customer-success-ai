"""Executive Dashboard Aggregation Service.

Orchestrates multi-source analytical queries across customers, interactions, and AI insights,
computing sentiment percentages, health score distributions, and caching results in Redis.
"""

from sqlalchemy.orm import Session
from app.config.logging import logger
from app.helpers import calculate_distribution_percentages
from app.models.customer import CustomerStatus
from app.repositories.customer_repository import CustomerRepository
from app.repositories.insight_repository import InsightRepository
from app.repositories.interaction_repository import InteractionRepository
from app.schemas import (
    CustomerResponse,
    DashboardSummaryResponse,
    HealthDistributionSchema,
    InteractionResponse,
    SentimentDistributionSchema,
    StatusDistributionSchema,
)
from app.services.cache_service import cache_service


class DashboardService:
    """Service aggregating customer success KPIs, sentiment breakdowns, and risk queues."""

    def __init__(self, db: Session):
        """Initialize DashboardService with database session and domain repositories.

        Args:
            db: Scoped SQLAlchemy database session.
        """
        self.db = db
        self.customer_repo = CustomerRepository(db)
        self.interaction_repo = InteractionRepository(db)
        self.insight_repo = InsightRepository(db)

    def get_summary(self) -> DashboardSummaryResponse:
        """Aggregate executive dashboard metrics with Redis caching.

        Queries customer health score buckets, interaction counts, sentiment percentages,
        at-risk customer accounts, and recent AI-flagged risk/action items.

        Returns:
            DashboardSummaryResponse: Fully populated executive dashboard data contract.
        """
        cache_key = "dashboard:summary"
        cached = cache_service.get(cache_key)
        if cached:
            logger.debug("[CACHE HIT] Dashboard summary retrieved from Redis")
            return DashboardSummaryResponse(**cached)

        logger.debug("[CACHE MISS] Aggregating dashboard summary from database")

        # 1. Customer metrics
        status_counts = self.customer_repo.get_status_counts()
        total_customers = sum(status_counts.values())
        active_customers = status_counts.get(CustomerStatus.ACTIVE.value, 0)
        at_risk_customers = status_counts.get(CustomerStatus.AT_RISK.value, 0)
        churned_customers = status_counts.get(CustomerStatus.CHURNED.value, 0)
        prospect_customers = status_counts.get(CustomerStatus.PROSPECT.value, 0)
        avg_health = self.customer_repo.get_average_health()
        health_dist_data = self.customer_repo.get_health_distribution()

        # 2. Interaction metrics
        total_interactions = self.interaction_repo.count_total()
        recent_interactions_models = self.interaction_repo.get_recent(limit=5)
        recent_interactions = [
            InteractionResponse.model_validate(i) for i in recent_interactions_models
        ]

        # 3. AI Insights metrics
        sentiment_counts = self.insight_repo.get_sentiment_distribution()
        percentages = calculate_distribution_percentages({
            "Positive": sentiment_counts.get("Positive", 0),
            "Neutral": sentiment_counts.get("Neutral", 0),
            "Negative": sentiment_counts.get("Negative", 0),
        })

        sentiment_dist = SentimentDistributionSchema(
            positive=sentiment_counts.get("Positive", 0),
            neutral=sentiment_counts.get("Neutral", 0),
            negative=sentiment_counts.get("Negative", 0),
            positive_percentage=percentages["Positive"],
            neutral_percentage=percentages["Neutral"],
            negative_percentage=percentages["Negative"],
        )

        health_dist = HealthDistributionSchema(
            healthy=health_dist_data.get("healthy", 0),
            moderate=health_dist_data.get("moderate", 0),
            critical=health_dist_data.get("critical", 0),
        )

        status_dist = StatusDistributionSchema(
            active=active_customers,
            at_risk=at_risk_customers,
            churned=churned_customers,
            prospect=prospect_customers,
        )

        at_risk_list_models = self.customer_repo.get_at_risk_customers(limit=5)
        at_risk_list = [CustomerResponse.model_validate(c) for c in at_risk_list_models]

        recent_risks = self.insight_repo.get_recent_risks(limit=6)
        recent_actions = self.insight_repo.get_recent_action_items(limit=6)

        dashboard_response = DashboardSummaryResponse(
            total_customers=total_customers,
            active_customers=active_customers,
            at_risk_customers=at_risk_customers,
            churned_customers=churned_customers,
            prospect_customers=prospect_customers,
            average_health_score=avg_health,
            total_interactions=total_interactions,
            recent_interactions_count=len(recent_interactions),
            sentiment_distribution=sentiment_dist,
            health_distribution=health_dist,
            status_distribution=status_dist,
            recent_interactions=recent_interactions,
            at_risk_customers_list=at_risk_list,
            recent_risks=recent_risks,
            recent_action_items=recent_actions,
        )

        # Cache in Redis
        try:
            cache_service.set(cache_key, dashboard_response.model_dump(mode="json"), ttl=60)
        except Exception as e:
            logger.warning(f"Failed to cache dashboard summary: {e}")

        return dashboard_response

