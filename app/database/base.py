"""
Database base configuration and session management.
Sets up SQLAlchemy engine, session factory, and base model.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from app.config.settings import settings # type: ignore
import os

# Create database directory if it doesn't exist
os.makedirs(os.path.dirname(settings.database_url.replace("sqlite:///./", "")), exist_ok=True)

# Create engine with SQLite-specific settings
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # Required for SQLite
    poolclass=StaticPool,  # Use static pool for SQLite
    echo=settings.database_echo  # Log SQL statements if DEBUG=True
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create base class for all models
Base = declarative_base()


def get_db():
    """
    Dependency injection function for database sessions.
    Yields a database session for each request.
    
    Yields:
        Session: SQLAlchemy session instance
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables.
    Call this once at application startup.
    """
    Base.metadata.create_all(bind=engine)