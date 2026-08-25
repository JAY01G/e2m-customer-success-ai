"""AI Intelligence and Automated Meeting Insights Service.

Handles prompt generation, AI LLM model invocation, structured schema validation,
resilient fallback handling, persistence of insight entities, and analytics cache eviction.
"""

import json
import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.config.settings import get_settings
from app.config.logging import logger
from app.helpers import clean_markdown_json
from app.models.ai_insight import AIInsight, GenerationStatus, SentimentType
from app.models.interaction import Interaction
from app.models.customer import Customer
from app.repositories.insight_repository import InsightRepository
from app.schemas import AIInsightSchema
from app.services.ai_provider import AIProvider, get_ai_provider
from app.services.cache_service import cache_service

settings = get_settings()


class AIService:
    """Service orchestrating AI insight extraction, validation, fallbacks, and caching."""

    def __init__(self, db: Session, provider: Optional[AIProvider] = None):
        """Initialize AIService with database session and configured AI Provider.

        Args:
            db: Scoped SQLAlchemy database session.
            provider: Optional AIProvider implementation (OpenAI, Anthropic, Mock).
        """
        self.db = db
        self.insight_repo = InsightRepository(db)
        self.provider = provider or get_ai_provider()

    def _parse_and_validate(self, raw_str: str) -> AIInsightSchema:
        """Parse raw JSON string from AI model and validate against Pydantic schema.

        Args:
            raw_str: Raw JSON or markdown-wrapped JSON string from AI provider.

        Returns:
            AIInsightSchema: Validated insight schema object.

        Raises:
            json.JSONDecodeError: If JSON syntax is malformed.
            pydantic.ValidationError: If payload does not match schema requirements.
        """
        cleaned = clean_markdown_json(raw_str)
        data = json.loads(cleaned)
        return AIInsightSchema.model_validate(data)

    def _create_fallback_insight(
        self, interaction: Interaction, customer_name: str, reason: str
    ) -> AIInsightSchema:
        """Generate a safe, deterministic fallback insight when the AI provider fails.

        Args:
            interaction: Target interaction model.
            customer_name: Name of customer.
            reason: Error or failure explanation.

        Returns:
            AIInsightSchema: Safe default schema with neutral sentiment.
        """
        logger.warning(f"Using fallback AI insight for interaction {interaction.id}. Reason: {reason}")
        return AIInsightSchema(
            summary=f"Meeting '{interaction.title}' recorded for {customer_name}. Automated AI analysis encountered a temporary provider issue.",
            sentiment="Neutral",
            action_items=[
                f"Review meeting notes for '{interaction.title}' manually",
                "Verify pending customer follow-ups and account status",
            ],
            risks=[],
        )

    async def generate_and_save_insight(
        self,
        interaction: Interaction,
        regenerate: bool = False,
    ) -> AIInsight:
        """Generate structured insights from meeting notes, validate schema, and persist to database.

        Args:
            interaction: Target Interaction ORM entity.
            regenerate: If True, bypasses existing insight cache to force re-analysis.

        Returns:
            AIInsight: Persisted AIInsight database entity.
        """
        # Check if insight already exists and regeneration is not requested
        existing = self.insight_repo.get_by_interaction_id(interaction.id)
        if existing and not regenerate and existing.generation_status == GenerationStatus.SUCCESS:
            logger.info(f"Returning existing insight for interaction {interaction.id}")
            return existing

        customer_name = interaction.customer.name if interaction.customer else "Customer"
        company_name = interaction.customer.company_name if interaction.customer else ""
        customer_context = f"{customer_name} ({company_name})"

        validated_schema: Optional[AIInsightSchema] = None
        status = GenerationStatus.SUCCESS
        max_retries = 2

        # Retry loop for AI provider call & JSON validation
        for attempt in range(1, max_retries + 1):
            try:
                raw_response = await self.provider.generate_insight_raw(
                    notes=interaction.notes,
                    title=interaction.title,
                    customer_context=customer_context,
                )
                validated_schema = self._parse_and_validate(raw_response)
                break
            except (json.JSONDecodeError, Exception) as e:
                logger.warning(
                    f"AI parsing/validation attempt {attempt}/{max_retries} failed for interaction {interaction.id}: {e}"
                )
                if attempt == max_retries:
                    status = GenerationStatus.FALLBACK
                    validated_schema = self._create_fallback_insight(
                        interaction, customer_name, str(e)
                    )

        if not validated_schema:
            status = GenerationStatus.FALLBACK
            validated_schema = self._create_fallback_insight(
                interaction, customer_name, "Unexpected AI generation failure"
            )

        # Map to database entity
        model_name = getattr(self.provider, "model", "mock-heuristic")
        sentiment_enum = SentimentType(validated_schema.sentiment)

        insight_entity = AIInsight(
            interaction_id=interaction.id,
            summary=validated_schema.summary,
            sentiment=sentiment_enum,
            action_items=validated_schema.action_items,
            risks=validated_schema.risks,
            model=model_name,
            generation_status=status,
        )

        persisted = self.insight_repo.create_or_update(insight_entity)

        # Invalidate dashboard metrics cache
        cache_service.invalidate_dashboard_cache()
        cache_service.invalidate_interaction_cache(str(interaction.id))

        return persisted

