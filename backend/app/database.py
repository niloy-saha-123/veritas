"""
Database setup and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import os

# Database URL - use SQLite for simplicity, can be changed to PostgreSQL
DATABASE_URL = settings.DATABASE_URL

# For SQLite, ensure the path is absolute and the directory exists
if "sqlite" in DATABASE_URL:
    # Extract path from SQLite URL (sqlite:///./veritas.db -> ./veritas.db)
    if DATABASE_URL.startswith("sqlite:///"):
        db_path = DATABASE_URL.replace("sqlite:///", "")
        # Make path absolute relative to backend directory
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if db_path.startswith("./"):
            db_path = os.path.join(backend_dir, db_path[2:])
        elif not os.path.isabs(db_path):
            db_path = os.path.join(backend_dir, db_path)
        # Ensure directory exists
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
