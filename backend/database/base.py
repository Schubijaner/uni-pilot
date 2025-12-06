"""SQLAlchemy base and database engine configuration.

IMPORTANT: This module is configured to use SQLite only.
Do not change the database backend without explicit permission.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

# SQLite database URL - DO NOT CHANGE without permission
# This project uses SQLite as the database backend
DATABASE_URL = "sqlite:///uni_pilot.db"

# Create engine with SQLite-specific configuration
# SQLite-specific settings are required and should not be changed for other databases
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite
    poolclass=StaticPool,  # Required for SQLite (doesn't support connection pooling)
    echo=False,  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base for models
Base = declarative_base()


def get_db():
    """Get database session (dependency for FastAPI)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables."""
    Base.metadata.drop_all(bind=engine)

