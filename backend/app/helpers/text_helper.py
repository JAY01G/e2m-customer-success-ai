"""Text Processing and Markdown Sanitization Helpers.

Provides string cleanup utilities for parsing LLM markdown JSON, string truncation,
and control character sanitization.
"""

import re


def clean_markdown_json(raw_str: str) -> str:
    """Strip markdown code block fences (```json, ```) from LLM output.

    Args:
        raw_str: String possibly wrapped in markdown code formatting.

    Returns:
        str: Raw JSON string without markdown code fences.
    """
    cleaned = raw_str.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate string to maximum character length with trailing ellipsis.

    Args:
        text: Input string.
        max_length: Maximum allowed character length.

    Returns:
        str: Truncated string with trailing ellipsis if shortened.
    """
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return f"{text[:max_length]}..."


def sanitize_string(text: str) -> str:
    """Strip dangerous ASCII control characters and normalize excess whitespace.

    Args:
        text: Input string.

    Returns:
        str: Cleaned string.
    """
    if not text:
        return ""
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    return " ".join(cleaned.split())

