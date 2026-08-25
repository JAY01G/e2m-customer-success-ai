"""Unit Tests for Pydantic Schema Validation Rules.

Validates boundary conditions, whitespace stripping, regex patterns, password complexity,
and range constraints across all domain schemas.
"""

import uuid
from datetime import datetime, timedelta
import pytest
from pydantic import ValidationError

from app.models.customer import CustomerStatus
from app.models.interaction import InteractionType
from app.models.user import UserRole
from app.schemas.auth import LoginRequest, RegisterRequest
from app.schemas.customer import CustomerCreate, CustomerFilterParams, CustomerUpdate
from app.schemas.insight import AIInsightSchema
from app.schemas.interaction import InteractionCreate, InteractionFilterParams, InteractionUpdate
from app.schemas.user import UserCreate, UserUpdate


# =========================================================================
# Customer Validation Tests
# =========================================================================

def test_customer_create_valid():
    """Test valid CustomerCreate model."""
    customer = CustomerCreate(
        name="  Alice Wonderland  ",
        company_name="  Wonderland Inc  ",
        email="Alice@EXAMPLE.com",
        phone="+1 (555) 123-4567",
        health_score=90,
        status=CustomerStatus.ACTIVE,
    )
    assert customer.name == "Alice Wonderland"
    assert customer.company_name == "Wonderland Inc"
    assert customer.email == "alice@example.com"
    assert customer.phone == "+1 (555) 123-4567"
    assert customer.health_score == 90


def test_customer_create_whitespace_only_rejected():
    """Ensure whitespace-only name and company_name raise ValidationError."""
    with pytest.raises(ValidationError) as exc:
        CustomerCreate(
            name="   ",
            company_name="Acme Corp",
            email="acme@example.com",
        )
    assert "name" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        CustomerCreate(
            name="Alice",
            company_name="   ",
            email="acme@example.com",
        )
    assert "company_name" in str(exc.value)


def test_customer_create_invalid_phone_rejected():
    """Ensure invalid phone number formats are rejected."""
    with pytest.raises(ValidationError) as exc:
        CustomerCreate(
            name="Alice",
            company_name="Acme Corp",
            email="acme@example.com",
            phone="not-a-phone-number",
        )
    assert "phone" in str(exc.value)


def test_customer_create_invalid_health_score():
    """Ensure health score must be between 0 and 100."""
    with pytest.raises(ValidationError):
        CustomerCreate(
            name="Alice",
            company_name="Acme Corp",
            email="acme@example.com",
            health_score=105,
        )

    with pytest.raises(ValidationError):
        CustomerCreate(
            name="Alice",
            company_name="Acme Corp",
            email="acme@example.com",
            health_score=-5,
        )


def test_customer_filter_params_health_score_range():
    """Ensure min_health_score cannot exceed max_health_score."""
    with pytest.raises(ValidationError) as exc:
        CustomerFilterParams(
            min_health_score=80,
            max_health_score=50,
        )
    assert "min_health_score" in str(exc.value)


def test_customer_filter_params_invalid_sort():
    """Ensure invalid sort_by and sort_order values are rejected."""
    with pytest.raises(ValidationError):
        CustomerFilterParams(sort_by="malicious_sql_column")

    with pytest.raises(ValidationError):
        CustomerFilterParams(sort_order="sideways")

    # Valid sort
    params = CustomerFilterParams(sort_by="company_name", sort_order="ASC")
    assert params.sort_by == "company_name"
    assert params.sort_order == "asc"


# =========================================================================
# Interaction Validation Tests
# =========================================================================

def test_interaction_create_valid():
    """Test valid InteractionCreate model."""
    customer_id = uuid.uuid4()
    interaction = InteractionCreate(
        customer_id=customer_id,
        title="  Quarterly Review  ",
        notes="  Discussion on product renewal and satisfaction.  ",
        duration_minutes=45,
        type=InteractionType.MEETING,
    )
    assert interaction.title == "Quarterly Review"
    assert interaction.notes == "Discussion on product renewal and satisfaction."
    assert interaction.duration_minutes == 45


def test_interaction_create_blank_title_rejected():
    """Ensure blank or short title is rejected."""
    customer_id = uuid.uuid4()
    with pytest.raises(ValidationError):
        InteractionCreate(
            customer_id=customer_id,
            title="   ",
            notes="Valid meeting notes here.",
        )


def test_interaction_create_blank_notes_rejected():
    """Ensure blank or short notes are rejected."""
    customer_id = uuid.uuid4()
    with pytest.raises(ValidationError):
        InteractionCreate(
            customer_id=customer_id,
            title="Valid Title",
            notes="    ",
        )


def test_interaction_duration_bounds():
    """Ensure duration_minutes is bounded between 1 and 1440."""
    customer_id = uuid.uuid4()
    with pytest.raises(ValidationError):
        InteractionCreate(
            customer_id=customer_id,
            title="Valid Title",
            notes="Valid meeting notes here.",
            duration_minutes=0,
        )

    with pytest.raises(ValidationError):
        InteractionCreate(
            customer_id=customer_id,
            title="Valid Title",
            notes="Valid meeting notes here.",
            duration_minutes=2000,
        )


def test_interaction_filter_params_date_range():
    """Ensure start_date cannot be after end_date."""
    now = datetime.now()
    with pytest.raises(ValidationError):
        InteractionFilterParams(
            start_date=now + timedelta(days=5),
            end_date=now,
        )


# =========================================================================
# Auth & Password Complexity Validation Tests
# =========================================================================

def test_register_password_complexity_rules():
    """Test password complexity validation for user registration."""
    # Too short (< 8 chars)
    with pytest.raises(ValidationError) as exc:
        RegisterRequest(name="User", email="u@e.com", password="P1!a")
    assert "password" in str(exc.value).lower()

    # Missing uppercase
    with pytest.raises(ValidationError) as exc:
        RegisterRequest(name="User", email="u@e.com", password="password123!")
    assert "uppercase" in str(exc.value)

    # Missing lowercase
    with pytest.raises(ValidationError) as exc:
        RegisterRequest(name="User", email="u@e.com", password="PASSWORD123!")
    assert "lowercase" in str(exc.value)

    # Missing number
    with pytest.raises(ValidationError) as exc:
        RegisterRequest(name="User", email="u@e.com", password="Password!!!!")
    assert "number" in str(exc.value)

    # Missing special character
    with pytest.raises(ValidationError) as exc:
        RegisterRequest(name="User", email="u@e.com", password="Password123")
    assert "special character" in str(exc.value)

    # Valid password
    reg = RegisterRequest(name="User", email="User@Example.COM", password="Password123!")
    assert reg.password == "Password123!"
    assert reg.email == "user@example.com"


# =========================================================================
# AI Insight Validation Tests
# =========================================================================

def test_ai_insight_schema_validation():
    """Test AIInsightSchema validation and list sanitization."""
    insight = AIInsightSchema(
        summary="  Customer expressed high satisfaction with recent features.  ",
        sentiment="Positive",
        action_items=["  Schedule Q4 review  ", "", "   ", "Send invoice"],
        risks=["  Risk of delay  ", ""],
    )
    assert insight.summary == "Customer expressed high satisfaction with recent features."
    assert insight.action_items == ["Schedule Q4 review", "Send invoice"]
    assert insight.risks == ["Risk of delay"]
