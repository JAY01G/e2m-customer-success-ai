from datetime import timedelta
import pytest
from app.exceptions.custom_exceptions import UnauthorizedException, ValidationException
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.utils.validators import validate_health_score, validate_password_strength


def test_password_hashing_and_verification():
    raw_password = "SecurePassword123!"
    hashed = get_password_hash(raw_password)

    assert hashed != raw_password
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword123!", hashed) is False


def test_password_strength_validator():
    # Valid password
    validate_password_strength("StrongPass1!")

    # Too short
    with pytest.raises(ValidationException, match="at least 8 characters"):
        validate_password_strength("Short1!")

    # Missing uppercase
    with pytest.raises(ValidationException, match="uppercase"):
        validate_password_strength("lowercase123!")

    # Missing lowercase
    with pytest.raises(ValidationException, match="lowercase"):
        validate_password_strength("UPPERCASE123!")

    # Missing number
    with pytest.raises(ValidationException, match="number"):
        validate_password_strength("NoNumbersHere!")

    # Missing special character
    with pytest.raises(ValidationException, match="special character"):
        validate_password_strength("NoSpecialChar123")


def test_health_score_validator():
    validate_health_score(0)
    validate_health_score(50)
    validate_health_score(100)

    with pytest.raises(ValidationException):
        validate_health_score(-1)

    with pytest.raises(ValidationException):
        validate_health_score(101)


def test_jwt_access_and_refresh_tokens():
    payload = {"sub": "1234-uuid", "email": "test@example.com", "role": "ADMIN"}
    access_token = create_access_token(payload)

    decoded = decode_token(access_token, expected_type="access")
    assert decoded["sub"] == "1234-uuid"
    assert decoded["email"] == "test@example.com"
    assert decoded["role"] == "ADMIN"
    assert decoded["type"] == "access"

    refresh_token = create_refresh_token(payload)
    decoded_refresh = decode_token(refresh_token, expected_type="refresh")
    assert decoded_refresh["sub"] == "1234-uuid"
    assert decoded_refresh["type"] == "refresh"

    # Mismatched type check
    with pytest.raises(UnauthorizedException, match="Invalid token type"):
        decode_token(access_token, expected_type="refresh")


def test_jwt_expired_token():
    payload = {"sub": "1234-uuid"}
    # Token expired 10 minutes ago
    expired_token = create_access_token(payload, expires_delta=timedelta(minutes=-10))

    with pytest.raises(UnauthorizedException, match="expired"):
        decode_token(expired_token, expected_type="access")


def test_jwt_invalid_token():
    with pytest.raises(UnauthorizedException, match="credentials"):
        decode_token("invalid.jwt.token.string", expected_type="access")
