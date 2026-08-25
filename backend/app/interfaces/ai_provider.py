"""AI Provider Interface Protocol.

Defines the contract for LLM vendors (OpenAI, Anthropic, Mock) to execute prompt
engineering and return raw JSON-structured customer meeting insights.
"""

from typing import Protocol


class IAIProvider(Protocol):
    """AI Provider Protocol for LLM vendors (OpenAI, Anthropic, Mock)."""

    async def generate_insight_raw(
        self,
        notes: str,
        title: str = "",
        customer_context: str = "",
    ) -> str:
        """Invoke AI model and return raw JSON-formatted completion string.

        Args:
            notes: Raw meeting notes or interaction transcript.
            title: Headline or topic of the interaction.
            customer_context: Customer company and business context string.

        Returns:
            str: JSON string conforming to AIInsightSchema structure.
        """
        ...

