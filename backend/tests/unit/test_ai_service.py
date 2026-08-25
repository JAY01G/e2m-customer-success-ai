import json
import pytest
from app.models.ai_insight import GenerationStatus, SentimentType
from app.models.customer import Customer
from app.models.interaction import Interaction
from app.schemas.insight import AIInsightSchema
from app.services.ai_provider import AIProvider, MockAIProvider
from app.services.ai_service import AIService


class FakeFailingProvider(AIProvider):
    async def generate_insight_raw(self, notes: str, title: str, customer_context: str) -> str:
        raise ConnectionError("AI Provider service timeout or unavailable")


class FakeMalformedJsonProvider(AIProvider):
    async def generate_insight_raw(self, notes: str, title: str, customer_context: str) -> str:
        return "{malformed-json-response: not valid"


class FakeInvalidSentimentProvider(AIProvider):
    async def generate_insight_raw(self, notes: str, title: str, customer_context: str) -> str:
        return json.dumps({
            "summary": "Meeting went well.",
            "sentiment": "SuperExcited",  # Invalid sentiment
            "action_items": ["Send report"],
            "risks": []
        })


class FakeValidProvider(AIProvider):
    async def generate_insight_raw(self, notes: str, title: str, customer_context: str) -> str:
        return "```json\n" + json.dumps({
            "summary": "Customer renewed their contract for another 2 years.",
            "sentiment": "Positive",
            "action_items": ["Send updated contract copy", "Schedule onboarding review"],
            "risks": []
        }) + "\n```"


@pytest.mark.asyncio
async def test_mock_ai_provider_positive():
    provider = MockAIProvider()
    raw = await provider.generate_insight_raw(
        notes="Customer is super happy with adoption and plans renewal expansion.",
        title="Renewal Discussion",
        customer_context="Acme Corp"
    )
    data = json.loads(raw)
    schema = AIInsightSchema.model_validate(data)
    assert schema.sentiment == "Positive"
    assert len(schema.action_items) > 0


@pytest.mark.asyncio
async def test_mock_ai_provider_negative_risks():
    provider = MockAIProvider()
    raw = await provider.generate_insight_raw(
        notes="Customer expressed frustration with bugs and threatened churn to competitor.",
        title="Escalation Call",
        customer_context="Nova Health"
    )
    data = json.loads(raw)
    schema = AIInsightSchema.model_validate(data)
    assert schema.sentiment == "Negative"
    assert len(schema.risks) > 0


@pytest.mark.asyncio
async def test_ai_service_success_flow(db_session, test_interaction):
    service = AIService(db=db_session, provider=FakeValidProvider())
    insight = await service.generate_and_save_insight(test_interaction)

    assert insight is not None
    assert insight.interaction_id == test_interaction.id
    assert insight.sentiment == SentimentType.Positive
    assert insight.generation_status == GenerationStatus.SUCCESS
    assert len(insight.action_items) == 2
    assert "renewed" in insight.summary.lower()


@pytest.mark.asyncio
async def test_ai_service_fallback_on_provider_error(db_session, test_interaction):
    service = AIService(db=db_session, provider=FakeFailingProvider())
    insight = await service.generate_and_save_insight(test_interaction)

    assert insight is not None
    assert insight.generation_status == GenerationStatus.FALLBACK
    assert insight.sentiment == SentimentType.Neutral
    assert len(insight.action_items) > 0


@pytest.mark.asyncio
async def test_ai_service_fallback_on_malformed_json(db_session, test_interaction):
    service = AIService(db=db_session, provider=FakeMalformedJsonProvider())
    insight = await service.generate_and_save_insight(test_interaction)

    assert insight is not None
    assert insight.generation_status == GenerationStatus.FALLBACK


@pytest.mark.asyncio
async def test_ai_service_fallback_on_invalid_sentiment(db_session, test_interaction):
    service = AIService(db=db_session, provider=FakeInvalidSentimentProvider())
    insight = await service.generate_and_save_insight(test_interaction)

    assert insight is not None
    assert insight.generation_status == GenerationStatus.FALLBACK


@pytest.mark.asyncio
async def test_ai_service_idempotency_without_regenerate(db_session, test_interaction):
    service = AIService(db=db_session, provider=FakeValidProvider())
    insight1 = await service.generate_and_save_insight(test_interaction, regenerate=False)
    insight2 = await service.generate_and_save_insight(test_interaction, regenerate=False)

    assert insight1.id == insight2.id
