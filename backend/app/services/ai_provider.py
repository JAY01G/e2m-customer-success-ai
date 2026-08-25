"""AI Provider Strategy Implementations.

Implements concrete LLM adapters for OpenAI (GPT-4o-mini), Anthropic (Claude-3.5-Haiku),
and a deterministic offline Mock AI Provider with heuristic sentiment and keyword analysis.
"""

from abc import ABC, abstractmethod
import json
import re
from typing import Any, Dict, Optional
import httpx
from openai import AsyncOpenAI, APIError as OpenAIBaseError, RateLimitError, AuthenticationError
from app.config.settings import get_settings
from app.config.logging import logger
from app.exceptions.custom_exceptions import AIServiceException

settings = get_settings()

AI_SYSTEM_PROMPT = """You are an expert enterprise Customer Success AI analyst.
Analyze the following customer interaction notes and return a strictly structured JSON object.

Output MUST follow this exact JSON schema:
{
  "summary": "Concise business-focused summary of the meeting/interaction (2-4 sentences)",
  "sentiment": "Positive" | "Neutral" | "Negative",
  "action_items": [
    "Actionable follow-up item 1",
    "Actionable follow-up item 2"
  ],
  "risks": [
    "Identified risk, churn factor, or blocker 1"
  ]
}

Rules:
1. Never invent facts or hallucinate details not mentioned in the notes.
2. The sentiment MUST be one of exact strings: "Positive", "Neutral", "Negative".
3. Return an empty array [] if there are no action items or risks.
4. Output ONLY raw valid JSON. No markdown code blocks, no explanation text outside the JSON.
"""


class AIProvider(ABC):
    """Abstract base class defining the AI provider interface."""

    @abstractmethod
    async def generate_insight_raw(
        self, notes: str, title: str, customer_context: str
    ) -> str:
        """Call AI model and return raw JSON string response.

        Args:
            notes: Meeting discussion notes or transcript.
            title: Headline or meeting topic.
            customer_context: Customer company and business context.

        Returns:
            str: Raw JSON string output.
        """
        pass


class OpenAIProvider(AIProvider):
    """OpenAI API integration using official AsyncOpenAI client."""

    def __init__(self):
        """Initialize OpenAI provider from application settings."""
        app_settings = get_settings()
        self.api_key = (app_settings.AI_API_KEY or getattr(app_settings, "OPENAI_API_KEY", None) or "").strip()
        self.model = app_settings.AI_MODEL or "gpt-4o-mini"
        self.timeout = float(app_settings.AI_TIMEOUT or 20)
        self.temperature = float(app_settings.AI_TEMPERATURE or 0.2)
        self.client = AsyncOpenAI(api_key=self.api_key, timeout=self.timeout) if self.api_key else None

    async def generate_insight_raw(
        self, notes: str, title: str, customer_context: str
    ) -> str:
        """Invoke OpenAI using official AsyncOpenAI SDK client.

        Args:
            notes: Meeting notes.
            title: Meeting title.
            customer_context: Customer company context.

        Returns:
            str: JSON string content from OpenAI.

        Raises:
            AIServiceException: If API key is missing, call times out, or error response is returned.
        """
        if not self.api_key or not self.client:
            raise AIServiceException("OpenAI API key is not configured")

        user_content = f"Customer Context: {customer_context}\nMeeting Title: {title}\nMeeting Notes:\n{notes}"

        try:
            logger.info(f"Invoking OpenAI API model '{self.model}' with AsyncOpenAI client...")
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": AI_SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"},
            )

            output_text = response.choices[0].message.content
            if not output_text:
                raise AIServiceException("OpenAI returned an empty response")
            return output_text
        except AuthenticationError as e:
            logger.error(f"OpenAI Authentication Error: {e.message}")
            raise AIServiceException(f"Invalid OpenAI API Key: {e.message}")
        except RateLimitError as e:
            logger.error(f"OpenAI Rate Limit / Quota Exceeded: {e.message}")
            raise AIServiceException(f"OpenAI Quota or Rate Limit exceeded: {e.message}")
        except OpenAIBaseError as e:
            logger.error(f"OpenAI API Error: {e.message}")
            raise AIServiceException(f"OpenAI API Error: {e.message}")
        except AIServiceException:
            raise
        except Exception as e:
            logger.error(f"OpenAI invocation failed: {e}")
            raise AIServiceException(f"AI generation failed: {str(e)}")



class AnthropicProvider(AIProvider):
    """Anthropic Claude API integration."""

    def __init__(self):
        """Initialize Anthropic provider from application settings."""
        app_settings = get_settings()
        self.api_key = (app_settings.AI_API_KEY or getattr(app_settings, "ANTHROPIC_API_KEY", None) or "").strip()
        self.model = app_settings.AI_MODEL or "claude-3-5-haiku-latest"
        self.timeout = app_settings.AI_TIMEOUT or 20
        self.temperature = app_settings.AI_TEMPERATURE or 0.2

    async def generate_insight_raw(
        self, notes: str, title: str, customer_context: str
    ) -> str:
        """Invoke Anthropic Messages API.

        Args:
            notes: Meeting notes.
            title: Meeting title.
            customer_context: Customer company context.

        Returns:
            str: JSON text output from Claude.

        Raises:
            AIServiceException: If API key is missing, call times out, or error response is returned.
        """
        if not self.api_key:
            raise AIServiceException("Anthropic API key is not configured")

        user_content = f"Customer Context: {customer_context}\nMeeting Title: {title}\nMeeting Notes:\n{notes}"
        payload = {
            "model": self.model,
            "system": AI_SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": user_content}],
            "max_tokens": 1000,
            "temperature": self.temperature,
        }
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    json=payload,
                    headers=headers,
                )
                if response.status_code != 200:
                    try:
                        err_json = response.json()
                        error_msg = err_json.get("error", {}).get("message") or response.text
                    except Exception:
                        error_msg = response.text
                    logger.error(f"Anthropic API error [{response.status_code}]: {error_msg}")
                    raise AIServiceException(f"Anthropic API error ({response.status_code}): {error_msg}")
                data = response.json()
                return data["content"][0]["text"]
        except httpx.TimeoutException:
            logger.error("Anthropic API call timed out")
            raise AIServiceException("AI service request timed out")
        except AIServiceException:
            raise
        except Exception as e:
            logger.error(f"Anthropic API invocation failed: {e}")
            raise AIServiceException(f"AI generation failed: {str(e)}")


class MockAIProvider(AIProvider):
    """Deterministic local AI provider for testing and development environments."""

    @staticmethod
    def analyze_heuristically(notes: str, title: str, customer_context: str) -> str:
        """Heuristically generate structured insight JSON offline without external network calls.

        Args:
            notes: Meeting notes.
            title: Meeting title.
            customer_context: Customer company context.

        Returns:
            str: Valid JSON string matching AIInsightSchema.
        """
        notes_lower = notes.lower() if notes else ""

        # Sentiment heuristics
        negative_keywords = ["churn", "unhappy", "frustrated", "cancel", "delay", "bug", "broken", "angry", "terrible", "issue", "risk", "competitor", "slow", "escalation"]
        positive_keywords = ["happy", "delighted", "renewal", "expand", "excited", "great", "love", "satisfaction", "smooth", "promoter", "excellent", "success", "delight"]

        neg_score = sum(1 for kw in negative_keywords if kw in notes_lower)
        pos_score = sum(1 for kw in positive_keywords if kw in notes_lower)

        if neg_score > pos_score:
            sentiment = "Negative"
        elif pos_score > neg_score:
            sentiment = "Positive"
        else:
            sentiment = "Neutral"

        # Action items extraction
        action_items = []
        if notes:
            for line in notes.split("\n"):
                clean_line = line.strip(" -*•\t")
                if any(prefix in clean_line.lower() for prefix in ["todo", "action", "follow up", "schedule", "send", "review", "share", "confirm", "provide"]):
                    action_items.append(clean_line)

        if not action_items:
            action_items = [
                f"Follow up with {customer_context or 'customer'} regarding discussed items in '{title}'",
                "Share recap notes and confirmed next steps with key stakeholders"
            ]

        # Risks extraction
        risks = []
        if sentiment == "Negative":
            risks.append(f"Customer expressed concerns during '{title}' requiring CSM escalation.")
        if "competitor" in notes_lower or "cancel" in notes_lower or "churn" in notes_lower:
            risks.append("Customer evaluating alternative solutions or considering contract cancellation.")
        if "bug" in notes_lower or "delay" in notes_lower or "downtime" in notes_lower:
            risks.append("Product issues or delivery delays threatening ongoing adoption.")

        # Summary creation
        first_sentence = notes.split(".")[0].strip() if (notes and "." in notes) else (notes[:120].strip() if notes else f"Discussion on {title}")
        summary = f"Interaction regarding '{title}'. {first_sentence}. Next steps and action plan recorded for account health tracking."

        result = {
            "summary": summary,
            "sentiment": sentiment,
            "action_items": action_items[:4],
            "risks": risks[:3],
        }
        return json.dumps(result)

    async def generate_insight_raw(
        self, notes: str, title: str, customer_context: str
    ) -> str:
        """Asynchronously invoke heuristic insight generator."""
        return self.analyze_heuristically(notes=notes, title=title, customer_context=customer_context)



def get_ai_provider() -> AIProvider:
    """Factory function instantiating the appropriate AIProvider based on environment configuration.

    Returns:
        AIProvider: Initialized OpenAIProvider, AnthropicProvider, or MockAIProvider instance.
    """
    app_settings = get_settings()
    provider_type = (app_settings.AI_PROVIDER or "mock").lower().strip()
    api_key = (app_settings.AI_API_KEY or getattr(app_settings, "OPENAI_API_KEY", None) or "").strip()

    if provider_type == "mock":
        logger.info("Initializing MockAIProvider (explicit mock mode configured)")
        return MockAIProvider()

    if provider_type == "openai":
        if api_key:
            logger.info("Initializing active OpenAIProvider")
            return OpenAIProvider()
        else:
            logger.warning("AI_PROVIDER is 'openai' but AI_API_KEY is empty. Falling back to MockAIProvider.")
            return MockAIProvider()
    elif provider_type == "anthropic":
        if api_key:
            logger.info("Initializing active AnthropicProvider")
            return AnthropicProvider()
        else:
            logger.warning("AI_PROVIDER is 'anthropic' but AI_API_KEY is empty. Falling back to MockAIProvider.")
            return MockAIProvider()
    else:
        logger.info(f"Unknown AI_PROVIDER '{provider_type}'. Defaulting to MockAIProvider.")
        return MockAIProvider()



