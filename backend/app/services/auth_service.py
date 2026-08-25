"""Authentication and Identity Service.

Orchestrates user registration, email validation, password hashing, credential checks,
and JWT access/refresh token generation.
"""

import uuid
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from app.config.settings import get_settings
from app.config.logging import logger
from app.exceptions.custom_exceptions import (
    ConflictException,
    UnauthorizedException,
    ValidationException,
)
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, AuthUserSummary
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.utils.validators import validate_password_strength

settings = get_settings()


class AuthService:
    """Service handling user account registration, login authentication, and token refreshes."""

    def __init__(self, db: Session):
        """Initialize AuthService with database session and UserRepository.

        Args:
            db: Scoped SQLAlchemy database session.
        """
        self.db = db
        self.user_repo = UserRepository(db)

    def register(self, req: RegisterRequest) -> Tuple[User, TokenResponse]:
        """Register a new user account, hash the password, and generate JWT tokens.

        Args:
            req: Registration request schema containing user details and password.

        Returns:
            Tuple[User, TokenResponse]: Created User ORM entity and JWT token response.

        Raises:
            ConflictException: If a user with the provided email already exists.
            ValidationException: If the password fails complexity criteria.
        """
        # Validate email uniqueness
        existing = self.user_repo.get_by_email(req.email)
        if existing:
            raise ConflictException("A user with this email address already exists")

        # Validate password strength
        validate_password_strength(req.password)

        hashed_password = get_password_hash(req.password)
        role = req.role if req.role else UserRole.CUSTOMER_SUCCESS_MANAGER

        new_user = User(
            name=req.name.strip(),
            email=req.email.lower().strip(),
            hashed_password=hashed_password,
            role=role,
            is_active=True,
        )

        user = self.user_repo.create(new_user)
        logger.info(f"User registered successfully: {user.email} (Role: {user.role})")

        token_response = self._generate_token_response(user)
        return user, token_response

    def login(self, req: LoginRequest) -> TokenResponse:
        """Authenticate user credentials and issue access/refresh token pair.

        Args:
            req: Login credentials request schema.

        Returns:
            TokenResponse: Token envelope with access and refresh JWTs.

        Raises:
            UnauthorizedException: If email/password are invalid or account is disabled.
        """
        user = self.user_repo.get_by_email(req.email)
        if not user or not verify_password(req.password, user.hashed_password):
            logger.warning(f"Failed login attempt for email: {req.email}")
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException("User account is inactive. Contact an administrator.")

        logger.info(f"User logged in: {user.email} (Role: {user.role})")
        return self._generate_token_response(user)

    def refresh(self, refresh_token: str) -> TokenResponse:
        """Validate refresh token and issue a fresh access token.

        Args:
            refresh_token: Signed refresh JWT string.

        Returns:
            TokenResponse: Updated token envelope.

        Raises:
            UnauthorizedException: If token is invalid, expired, or user is inactive.
        """
        payload = decode_token(refresh_token, expected_type="refresh")
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Invalid refresh token")

        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise UnauthorizedException("Invalid token subject")

        user = self.user_repo.get_by_id(user_uuid)
        if not user or not user.is_active:
            raise UnauthorizedException("User no longer exists or is inactive")

        return self._generate_token_response(user)

    def _generate_token_response(self, user: User) -> TokenResponse:
        """Generate signed access and refresh tokens for a user.

        Args:
            user: Authenticated User model instance.

        Returns:
            TokenResponse: Complete token response payload.
        """
        token_payload = {
            "sub": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role.value if hasattr(user.role, "value") else str(user.role),
        }
        access_token = create_access_token(token_payload)
        refresh_token = create_refresh_token(token_payload)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_token=refresh_token,
            user=AuthUserSummary(
                id=user.id,
                name=user.name,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
            ),
        )

