"""Database Session Fastapi Dependencies.

Provides dependency injection providers for scoped SQLAlchemy database sessions.
"""

from typing import Generator
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.config.logging import logger


def get_db() -> Generator[Session, None, None]:
    """Provide a transactional SQLAlchemy database session.

    Yields a database session instance, handling automatic rollback in the
    event of unhandled exceptions and ensuring connection cleanup upon request completion.

    Yields:
        Session: Active SQLAlchemy database session.

    Raises:
        Exception: Re-raises any exception encountered during request handling.
    """
    db: Session = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session exception occurred, rolling back: {e}")
        db.rollback()
        raise
    finally:
        db.close()

