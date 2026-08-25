"""Authentication API Router.

Mounts endpoints for user registration, credentials login, refresh token rotation,
and current user profile inspection.
"""

from typing import Optional
from fastapi import APIRouter, Body, Cookie, Depends, Response, status
from sqlalchemy.orm import Session
from app.controllers.auth_controller import AuthController
from app.database.dependencies import get_db
from app.dependencies.auth import get_current_active_user
from app.exceptions.custom_exceptions import UnauthorizedException
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    AuthUserSummary,
    RefreshTokenRequest,
)
from app.schemas.common import APIResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    response_description="Newly created user profile and initial JWT access token",
)
def register(
    req: RegisterRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    """Register a new user account with validated credentials and return access/refresh tokens.

    Args:
        req: Registration request payload.
        response: FastAPI response object for setting HttpOnly refresh cookie.
        db: Scoped database session.

    Returns:
        APIResponse[TokenResponse]: Envelope with JWT credentials.
    """
    return AuthController.register(req=req, db=db, response=response)


@router.post(
    "/login",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Authenticate and receive JWT access token",
    response_description="Authenticated user credentials and JWT access token",
)
def login(
    req: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    """Authenticate user with email and password, issuing access and refresh tokens.

    Args:
        req: Login credentials payload.
        response: FastAPI response object for setting HttpOnly refresh cookie.
        db: Scoped database session.

    Returns:
        APIResponse[TokenResponse]: Envelope with JWT credentials.
    """
    return AuthController.login(req=req, db=db, response=response)


@router.post(
    "/refresh",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Refresh access token using HttpOnly cookie or body",
    response_description="Refreshed JWT access token credentials",
)
def refresh(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    req: Optional[RefreshTokenRequest] = Body(None),
    db: Session = Depends(get_db),
):
    """Rotate and refresh access token using the HttpOnly cookie or request body.

    Args:
        response: FastAPI response object.
        refresh_token: Refresh token extracted from cookie.
        req: Optional refresh token payload from body.
        db: Scoped database session.

    Returns:
        APIResponse[TokenResponse]: Fresh token envelope.
    """
    token = refresh_token
    if not token and req and req.refresh_token:
        token = req.refresh_token

    if not token:
        raise UnauthorizedException("Refresh token is missing")
    return AuthController.refresh(refresh_token=token, db=db, response=response)


@router.get(
    "/me",
    response_model=APIResponse[AuthUserSummary],
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user profile",
    response_description="Profile details, permissions, and role of the authenticated user",
)
def get_me(
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve identity and permissions for the currently authenticated user.

    Args:
        current_user: Authenticated active user model from dependency.

    Returns:
        APIResponse[AuthUserSummary]: Current user profile summary.
    """
    return AuthController.me(current_user=current_user)


