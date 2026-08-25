"""Database Engine and Session Configuration Module.

Configures the SQLAlchemy engine, connection pooling parameters, session
factory (`SessionLocal`), and database initialization routines for PostgreSQL/SQLite.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config.settings import get_settings
from app.config.logging import logger

settings = get_settings()

# Normalize sqlite/postgres URLs for SQLAlchemy 2.0
db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Handle sqlite specific connect args for local tests
connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    db_url,
    echo=settings.DEBUG,
    connect_args=connect_args,
    pool_pre_ping=True,
    **({"pool_size": 10, "max_overflow": 20} if not db_url.startswith("sqlite") else {})
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


def init_db() -> None:
    """Initialize database tables from DeclarativeBase metadata.

    Imports all models to ensure complete registry population before executing
    DDL creation against the target database engine.
    """
    from app.database.base import Base
    import app.models  # Ensure all models are registered
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully.")

