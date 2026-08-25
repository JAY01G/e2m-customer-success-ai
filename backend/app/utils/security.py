"""Security and Cryptographic Utilities.

Handles Argon2 password hashing, password verification, JWT access and refresh token
generation, signing, decoding, and signature validation.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import jwt
from passlib.context import CryptContext
from app.config.settings import get_settings
from app.exceptions.custom_exceptions import UnauthorizedException

settings = get_settings()

pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
    argon2__memory_cost=65536,
    argon2__time_cost=3,
    argon2__parallelism=4,
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored cryptographic hash.

    Args:
        plain_password: Cleartext password string.
        hashed_password: Stored Argon2/Bcrypt hash.

    Returns:
        bool: True if password matches hash, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a secure Argon2 hash for the given plaintext password.

    Args:
        password: Plaintext password.

    Returns:
        str: Argon2 hashed password string.
    """
    return pwd_context.hash(password)


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create a signed JWT access token containing subject and expiration claims.

    Args:
        data: Claims payload dictionary (must include 'sub').
        expires_delta: Optional custom lifetime duration.

    Returns:
        str: Encoded JWT access token string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc), "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create a signed JWT refresh token with unique jti identifier.

    Args:
        data: Claims payload dictionary.
        expires_delta: Optional custom lifetime duration.

    Returns:
        str: Encoded JWT refresh token string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
        "jti": str(uuid.uuid4())
    })
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str, expected_type: str = "access") -> Dict[str, Any]:
    """Decode, verify signature, and validate token type claim.

    Args:
        token: Encoded JWT string.
        expected_type: Expected 'type' claim ('access' or 'refresh').

    Returns:
        Dict[str, Any]: Decoded token claims payload dictionary.

    Raises:
        UnauthorizedException: If token has expired, signature is invalid, or type mismatches.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        token_type = payload.get("type")
        if token_type != expected_type:
            raise UnauthorizedException(f"Invalid token type: expected {expected_type}")
        return payload
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException("Token has expired")
    except jwt.InvalidTokenError:
        raise UnauthorizedException("Could not validate credentials")

