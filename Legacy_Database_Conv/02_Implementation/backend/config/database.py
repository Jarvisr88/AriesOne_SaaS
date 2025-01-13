"""
Database configuration and connection management.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from typing import Generator
from contextlib import contextmanager
import os

# Database configuration
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:postgres@localhost:5432/ariesone'
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=5,         # Set connection pool size
    max_overflow=10      # Allow up to 10 connections beyond pool_size
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Get database session with automatic cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db(engine: Engine) -> None:
    """Initialize database schema."""
    from app.models.base import Base
    Base.metadata.create_all(bind=engine)

def get_engine() -> Engine:
    """Get SQLAlchemy engine instance."""
    return engine
