"""
Database configuration and session management
Using SQLModel with SQLite for persistent storage
"""

from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os

# Import models to ensure they are registered with SQLModel
from models import Product, PriceHistory

# Database file path
DATABASE_FILE = "amazon_scraper.db"
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# Create engine
# connect_args={"check_same_thread": False} is needed for SQLite with FastAPI
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    connect_args={"check_same_thread": False}
)


def create_db_and_tables():
    """
    Create all database tables if they don't exist

    This function should be called on application startup to ensure
    the database schema is properly initialized.
    """
    SQLModel.metadata.create_all(engine)
    print(f"✓ Database initialized: {DATABASE_FILE}")


def get_session() -> Generator[Session, None, None]:
    """
    Dependency function to get a database session

    Yields:
        Session: SQLModel database session

    Usage in FastAPI:
        @app.get("/items/")
        def read_items(session: Session = Depends(get_session)):
            ...
    """
    with Session(engine) as session:
        yield session


def drop_all_tables():
    """
    Drop all tables - USE WITH CAUTION!

    This function is useful for development/testing to reset the database.
    Should not be used in production.
    """
    SQLModel.metadata.drop_all(engine)
    print("⚠ All tables dropped")


def get_db_info():
    """
    Get information about the database

    Returns:
        dict: Database information including file path and size
    """
    db_exists = os.path.exists(DATABASE_FILE)
    db_size = os.path.getsize(DATABASE_FILE) if db_exists else 0

    return {
        "database_file": DATABASE_FILE,
        "database_url": DATABASE_URL,
        "exists": db_exists,
        "size_bytes": db_size,
        "size_mb": round(db_size / (1024 * 1024), 2) if db_size > 0 else 0
    }


if __name__ == "__main__":
    # When run directly, create the database tables
    print("Creating database tables...")
    create_db_and_tables()
    print("\nDatabase info:")
    info = get_db_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
