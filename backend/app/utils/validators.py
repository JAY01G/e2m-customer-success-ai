"""Input and Business Rule Validation Utilities.

Provides validation functions for password complexity rules and customer health score ranges.
"""

import re
from app.exceptions.custom_exceptions import ValidationException


def validate_password_strength(password: str) -> None:
    """Validate that password meets security complexity rules.

    Rules enforced:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character

    Args:
        password: Cleartext password to test.

    Raises:
        ValidationException: If password fails any complexity criterion.
    """
    if len(password) < 8:
        raise ValidationException("Password must be at least 8 characters long")
    if not re.search(r"[A-Z]", password):
        raise ValidationException("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        raise ValidationException("Password must contain at least one lowercase letter")
    if not re.search(r"\d", password):
        raise ValidationException("Password must contain at least one number")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\/]", password):
        raise ValidationException("Password must contain at least one special character")


def validate_health_score(score: int) -> None:
    """Ensure customer health score falls within the valid 0-100 range.

    Args:
        score: Health score integer.

    Raises:
        ValidationException: If score is less than 0 or greater than 100.
    """
    if score < 0 or score > 100:
        raise ValidationException("Health score must be between 0 and 100")

