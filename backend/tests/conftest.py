import os
import sys
import uuid
from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.settings import get_settings
from app.database.base import Base
from app.database.dependencies import get_db
from app.main import app
from app.models.ai_insight import AIInsight, GenerationStatus, SentimentType
from app.models.customer import Customer, CustomerStatus
from app.models.interaction import Interaction, InteractionType
from app.models.user import User, UserRole
from app.services.ai_provider import MockAIProvider
from app.services.cache_service import cache_service
from app.utils.security import create_access_token, get_password_hash

# In-memory SQLite engine for tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine, expire_on_commit=False
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    # Disable live Redis connection during tests and enforce mock AI
    cache_service.enabled = False
    cache_service._client = None
    os.environ["AI_PROVIDER"] = "mock"
    os.environ["JWT_SECRET"] = "test-secret-key-for-unit-and-integration-tests"


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_admin_user(db_session: Session) -> User:
    user = User(
        name="Admin User",
        email="admin@test.com",
        hashed_password=get_password_hash("Password123!"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_csm_user(db_session: Session) -> User:
    user = User(
        name="CSM User",
        email="csm@test.com",
        hashed_password=get_password_hash("Password123!"),
        role=UserRole.CUSTOMER_SUCCESS_MANAGER,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_viewer_user(db_session: Session) -> User:
    user = User(
        name="Viewer User",
        email="viewer@test.com",
        hashed_password=get_password_hash("Password123!"),
        role=UserRole.VIEWER,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_headers(test_admin_user: User) -> dict:
    token = create_access_token({
        "sub": str(test_admin_user.id),
        "email": test_admin_user.email,
        "name": test_admin_user.name,
        "role": test_admin_user.role.value,
    })
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def csm_headers(test_csm_user: User) -> dict:
    token = create_access_token({
        "sub": str(test_csm_user.id),
        "email": test_csm_user.email,
        "name": test_csm_user.name,
        "role": test_csm_user.role.value,
    })
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def viewer_headers(test_viewer_user: User) -> dict:
    token = create_access_token({
        "sub": str(test_viewer_user.id),
        "email": test_viewer_user.email,
        "name": test_viewer_user.name,
        "role": test_viewer_user.role.value,
    })
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_customer(db_session: Session, test_csm_user: User) -> Customer:
    customer = Customer(
        name="Jane Doe",
        company_name="Acme Corp",
        email="jane@acme.com",
        phone="+1234567890",
        industry="SaaS",
        status=CustomerStatus.ACTIVE,
        health_score=85,
        owner_id=test_csm_user.id,
        notes="High-growth account",
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer


@pytest.fixture
def test_interaction(db_session: Session, test_customer: Customer, test_csm_user: User) -> Interaction:
    interaction = Interaction(
        customer_id=test_customer.id,
        user_id=test_csm_user.id,
        type=InteractionType.MEETING,
        title="Quarterly Review",
        notes="Customer expressed great satisfaction with the platform. Action item: send new feature roadmap.",
        duration_minutes=45,
    )
    db_session.add(interaction)
    db_session.commit()
    db_session.refresh(interaction)
    return interaction
