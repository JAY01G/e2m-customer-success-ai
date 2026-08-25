"""Unit tests for Global Exception and Error Handlers."""

import pytest
from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.middleware.error_handler import register_exception_handlers
from app.exceptions.custom_exceptions import (
    AppException,
    NotFoundException,
    UnauthorizedException,
    ForbiddenException,
    BadRequestException,
    ConflictException,
    ValidationException,
    AIServiceException,
)


@pytest.fixture
def error_test_app():
    """Create a minimal FastAPI test application with error handlers registered."""
    test_app = FastAPI()
    register_exception_handlers(test_app)

    @test_app.get("/test-not-found")
    def raise_not_found():
        raise NotFoundException("Customer not found", errors=[{"id": "c123"}])

    @test_app.get("/test-unauthorized")
    def raise_unauthorized():
        raise UnauthorizedException("Invalid token provided")

    @test_app.get("/test-forbidden")
    def raise_forbidden():
        raise ForbiddenException("Admin privilege required")

    @test_app.get("/test-conflict")
    def raise_conflict():
        raise ConflictException("Email address already registered")

    @test_app.get("/test-ai-service")
    def raise_ai_service():
        raise AIServiceException("AI Gateway timed out")

    @test_app.get("/test-starlette-http")
    def raise_starlette_http():
        raise StarletteHTTPException(status_code=404, detail="Page does not exist")

    @test_app.get("/test-value-error")
    def raise_value_error():
        raise ValueError("Invalid score value")

    @test_app.get("/test-key-error")
    def raise_key_error():
        raise KeyError("missing_field")

    @test_app.get("/test-integrity-error")
    def raise_integrity():
        raise IntegrityError("INSERT INTO users...", params={}, orig=Exception("UNIQUE constraint failed: users.email"))

    @test_app.get("/test-sqlalchemy-error")
    def raise_sqlalchemy():
        raise SQLAlchemyError("Connection reset by peer")

    @test_app.get("/test-unhandled-exception")
    def raise_unhandled():
        raise RuntimeError("Unexpected server crash")

    return test_app


@pytest.fixture
def error_client(error_test_app):
    return TestClient(error_test_app, raise_server_exceptions=False)


def test_not_found_exception_handling(error_client):
    response = error_client.get("/test-not-found")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["data"] is None
    assert json_data["message"] == "Customer not found"
    assert json_data["errors"] == [{"id": "c123"}]


def test_unauthorized_exception_handling(error_client):
    response = error_client.get("/test-unauthorized")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["message"] == "Invalid token provided"


def test_forbidden_exception_handling(error_client):
    response = error_client.get("/test-forbidden")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["message"] == "Admin privilege required"


def test_conflict_exception_handling(error_client):
    response = error_client.get("/test-conflict")
    assert response.status_code == status.HTTP_409_CONFLICT
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["message"] == "Email address already registered"


def test_ai_service_exception_handling(error_client):
    response = error_client.get("/test-ai-service")
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["message"] == "AI Gateway timed out"


def test_starlette_http_exception_handling(error_client):
    response = error_client.get("/test-starlette-http")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    json_data = response.json()
    assert json_data["success"] is False
    assert json_data["message"] == "Page does not exist"


def test_value_error_handling(error_client):
    response = error_client.get("/test-value-error")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert "Invalid score value" in json_data["message"]


def test_key_error_handling(error_client):
    response = error_client.get("/test-key-error")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data["success"] is False
    assert "missing_field" in json_data["message"]


def test_integrity_error_handling(error_client):
    response = error_client.get("/test-integrity-error")
    assert response.status_code == status.HTTP_409_CONFLICT
    json_data = response.json()
    assert json_data["success"] is False
    assert "already exists" in json_data["message"]


def test_sqlalchemy_error_handling(error_client):
    response = error_client.get("/test-sqlalchemy-error")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    json_data = response.json()
    assert json_data["success"] is False
    assert "database error occurred" in json_data["message"].lower()


def test_unhandled_exception_handling(error_client):
    response = error_client.get("/test-unhandled-exception")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    json_data = response.json()
    assert json_data["success"] is False
    assert "unexpected internal server error" in json_data["message"].lower()
