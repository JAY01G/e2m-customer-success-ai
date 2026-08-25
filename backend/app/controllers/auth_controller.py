"""Authentication HTTP Controller.

Handles HTTP protocol details for user registration, login authentication,
cookie-based refresh token assignment, and profile inspection.
"""

from fastapi import Response
from sqlalchemy.orm import Session
from app.config.settings import get_settings
from app.helpers import api_response
from app.models.user import User
from app.schemas import (
    APIResponse,
    AuthUserSummary,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)
from app.services.auth_service import AuthService

settings = get_settings()


class AuthController:
    """Controller handling authentication requests and secure cookie lifecycle."""

    @staticmethod
    def register(req: RegisterRequest, db: Session, response: Response) -> APIResponse[TokenResponse]:
        """Process user registration and attach secure refresh cookie.

        Args:
            req: Registration payload.
            db: Database session.
            response: FastAPI response object for cookie manipulation.

        Returns:
            APIResponse[TokenResponse]: Success API envelope with JWT tokens.
        """
        service = AuthService(db)
        user, token_response = service.register(req)

        # Set secure HttpOnly refresh token cookie
        if token_response.refresh_token:
            response.set_cookie(
                key="refresh_token",
                value=token_response.refresh_token,
                httponly=True,
                secure=settings.APP_ENV == "production",
                samesite="lax",
                max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
                path="/api/v1/auth",
            )

        return api_response(
            data=token_response,
            message="User registered successfully",
        )

    @staticmethod
    def login(req: LoginRequest, db: Session, response: Response) -> APIResponse[TokenResponse]:
        """Authenticate user credentials and attach secure refresh cookie.

        Args:
            req: Login credentials payload.
            db: Database session.
            response: FastAPI response object.

        Returns:
            APIResponse[TokenResponse]: Success API envelope with JWT tokens.
        """
        service = AuthService(db)
        token_response = service.login(req)

        # Set secure HttpOnly refresh token cookie
        if token_response.refresh_token:
            response.set_cookie(
                key="refresh_token",
                value=token_response.refresh_token,
                httponly=True,
                secure=settings.APP_ENV == "production",
                samesite="lax",
                max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
                path="/api/v1/auth",
            )

        return api_response(
            data=token_response,
            message="Login successful",
        )

    @staticmethod
    def refresh(refresh_token: str, db: Session, response: Response) -> APIResponse[TokenResponse]:
        """Issue new access token from refresh token and update refresh cookie.

        Args:
            refresh_token: Refresh token string.
            db: Database session.
            response: FastAPI response object.

        Returns:
            APIResponse[TokenResponse]: Success API envelope with fresh access token.
        """
        service = AuthService(db)
        token_response = service.refresh(refresh_token)

        if token_response.refresh_token:
            response.set_cookie(
                key="refresh_token",
                value=token_response.refresh_token,
                httponly=True,
                secure=settings.APP_ENV == "production",
                samesite="lax",
                max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
                path="/api/v1/auth",
            )

        return api_response(
            data=token_response,
            message="Token refreshed successfully",
        )

    @staticmethod
    def me(current_user: User) -> APIResponse[AuthUserSummary]:
        """Return profile information of currently authenticated user.

        Args:
            current_user: Resolved authenticated User model.

        Returns:
            APIResponse[AuthUserSummary]: User profile summary envelope.
        """
        summary = AuthUserSummary(
            id=current_user.id,
            name=current_user.name,
            email=current_user.email,
            role=current_user.role,
            is_active=current_user.is_active,
        )
        return api_response(
            data=summary,
            message="Current user profile retrieved",
        )

