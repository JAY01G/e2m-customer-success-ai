"""Customer Telemetry and Health Score Helpers.

Provides categorization rules for health scores and proportional distribution calculators.
"""

from typing import Dict
from app.types import HealthCategoryLiteral


def categorize_health_score(score: int) -> HealthCategoryLiteral:
    """Categorize numeric health score (0-100) into business telemetry tier.

    Tiers:
    - 80-100: Healthy
    - 50-79: Moderate
    - 0-49: Critical

    Args:
        score: Numeric health score integer.

    Returns:
        HealthCategoryLiteral: 'Healthy', 'Moderate', or 'Critical'.
    """
    if score >= 80:
        return "Healthy"
    elif score >= 50:
        return "Moderate"
    return "Critical"


def calculate_distribution_percentages(counts: Dict[str, int]) -> Dict[str, float]:
    """Calculate normalized, rounded percentages from a category counts dictionary.

    Args:
        counts: Dictionary mapping category names to counts.

    Returns:
        Dict[str, float]: Dictionary mapping category names to 1-decimal percentage floats.
    """
    total = sum(counts.values())
    if total == 0:
        return {key: 0.0 for key in counts}
    return {key: round((val / total) * 100, 1) for key, val in counts.items()}

