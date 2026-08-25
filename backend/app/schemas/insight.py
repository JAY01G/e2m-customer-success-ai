"""AI Insight Request, Response, and Provider Contract Schemas.

Defines Pydantic models for structured LLM insight generation, serializable insight responses,
and on-demand re-analysis triggers with robust data validation.
"""

import uuid
from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.models.ai_insight import GenerationStatus, SentimentType


class AIInsightSchema(BaseModel):
    """Pydantic schema used to validate structured JSON returned from AI provider."""

    summary: str = Field(..., min_length=5, max_length=10000, description="Executive business-oriented summary")
    sentiment: Literal["Positive", "Neutral", "Negative"] = Field(
        ..., description="Sentiment classification: Positive, Neutral, or Negative"
    )
    action_items: List[str] = Field(
        default_factory=list, description="Extracted actionable follow-ups"
    )
    risks: List[str] = Field(
        default_factory=list, description="Identified customer risks, blockers, or churn flags"
    )

    @field_validator("summary")
    @classmethod
    def validate_summary(cls, v: str) -> str:
        """Validate that summary is not whitespace only."""
        trimmed = v.strip()
        if len(trimmed) < 5:
            raise ValueError("Summary must be at least 5 characters long and cannot be whitespace only")
        return trimmed

    @field_validator("action_items", "risks")
    @classmethod
    def clean_string_list(cls, v: List[str]) -> List[str]:
        """Strip and remove empty items from string lists."""
        cleaned = []
        for item in v:
            if isinstance(item, str):
                trimmed = item.strip()
                if trimmed:
                    cleaned.append(trimmed)
        return cleaned


class AIInsightResponse(BaseModel):
    """Schema for AI Insight representation returned in API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    interaction_id: uuid.UUID
    summary: str
    sentiment: SentimentType
    action_items: List[str]
    risks: List[str]
    model: str
    generation_status: GenerationStatus
    created_at: datetime
    updated_at: datetime


class AIInsightGenerateRequest(BaseModel):
    """Schema for requesting on-demand AI analysis for an interaction."""

    regenerate: bool = Field(
        default=False, description="If true, generates a new insight even if one already exists"
    )
