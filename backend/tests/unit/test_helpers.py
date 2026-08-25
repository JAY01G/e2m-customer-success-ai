import pytest
from datetime import datetime, timezone
from app.helpers.response import api_response, paginated_api_response, error_api_response
from app.helpers.datetime_helper import utc_now, format_iso, parse_iso
from app.helpers.text_helper import clean_markdown_json, truncate_text, sanitize_string
from app.helpers.telemetry_helper import categorize_health_score, calculate_distribution_percentages


def test_api_response_helper():
    res = api_response(data={"key": "value"}, message="Test success")
    assert res.success is True
    assert res.data == {"key": "value"}
    assert res.message == "Test success"
    assert res.errors is None


def test_paginated_api_response_helper():
    items = ["item1", "item2", "item3"]
    res = paginated_api_response(items=items, total=10, page=1, page_size=3)
    assert res.success is True
    assert res.data.total == 10
    assert res.data.total_pages == 4
    assert len(res.data.items) == 3


def test_error_api_response_helper():
    res = error_api_response(message="Invalid input", errors=["Field required"])
    assert res.success is False
    assert res.data is None
    assert res.message == "Invalid input"
    assert res.errors == ["Field required"]


def test_datetime_helpers():
    now = utc_now()
    assert now.tzinfo == timezone.utc

    iso_str = format_iso(now)
    assert isinstance(iso_str, str)

    parsed = parse_iso(iso_str)
    assert parsed.year == now.year


def test_text_helpers():
    # Markdown JSON cleaner
    raw_markdown = "```json\n{\"summary\": \"Test\"}\n```"
    cleaned = clean_markdown_json(raw_markdown)
    assert cleaned == '{"summary": "Test"}'

    # Truncate text
    long_text = "The quick brown fox jumps over the lazy dog"
    assert truncate_text(long_text, 15) == "The quick brown..."
    assert truncate_text("Short", 10) == "Short"

    # Sanitize string
    dirty = "Hello \x00 World \n\n Test"
    assert sanitize_string(dirty) == "Hello World Test"


def test_telemetry_helpers():
    # Health score categorization
    assert categorize_health_score(90) == "Healthy"
    assert categorize_health_score(80) == "Healthy"
    assert categorize_health_score(79) == "Moderate"
    assert categorize_health_score(50) == "Moderate"
    assert categorize_health_score(49) == "Critical"
    assert categorize_health_score(0) == "Critical"

    # Distribution percentages
    counts = {"Positive": 6, "Neutral": 3, "Negative": 1}
    percentages = calculate_distribution_percentages(counts)
    assert percentages["Positive"] == 60.0
    assert percentages["Neutral"] == 30.0
    assert percentages["Negative"] == 10.0

    # Zero distribution safety
    zero_counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
    zero_percentages = calculate_distribution_percentages(zero_counts)
    assert zero_percentages["Positive"] == 0.0
