"""Database Engine and Session Configuration Module.

Configures the SQLAlchemy engine, connection pooling parameters, session
factory (`SessionLocal`), and database initialization routines for PostgreSQL/SQLite.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool, StaticPool
from app.config.settings import get_settings
from app.config.logging import logger

settings = get_settings()

db_url = settings.DATABASE_URL
IS_VERCEL = os.getenv("VERCEL") == "1" or os.getenv("AWS_LAMBDA_FUNCTION_NAME") is not None

# On Vercel Serverless, if DATABASE_URL is localhost, fallback gracefully to /tmp SQLite
if IS_VERCEL and ("localhost" in db_url or "127.0.0.1" in db_url):
    db_url = "sqlite:////tmp/customer_success.db"
    logger.info(f"Vercel Serverless environment detected with local DB. Fallback to {db_url}")

# Normalize postgres URL for SQLAlchemy 2.0
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        db_url,
        echo=settings.DEBUG,
        connect_args=connect_args,
        poolclass=StaticPool,
    )
else:
    # Use 5s timeout and NullPool for serverless PostgreSQL
    connect_args = {"connect_timeout": 5}
    engine = create_engine(
        db_url,
        echo=settings.DEBUG,
        connect_args=connect_args,
        poolclass=NullPool if IS_VERCEL else None,
        pool_pre_ping=True,
        **({} if IS_VERCEL else {"pool_size": 10, "max_overflow": 20}),
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
    try:
        from app.database.base import Base
        import app.models  # Ensure all models are registered
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.warning(f"Database initialization deferred/warning: {e}")


