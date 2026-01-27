"""
Database Dependencies
=====================

FastAPI dependencies for database session management.
"""

import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URLs
MAIN_DB_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/sentry_burnout_db")
VECTOR_DB_URL = os.getenv("VECTOR_DB_URL", "postgresql://user:password@localhost:5432/sentry_vector_db")

# Create database engine
engine = create_engine(MAIN_DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.

    Yields:
        SQLAlchemy Session

    Usage:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Use db here
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
