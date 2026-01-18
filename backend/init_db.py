"""
Initialize database tables.
Run this script once to create the database schema.
"""

from app.database import Base, engine
from app.models.database_models import User, UserToken

if __name__ == "__main__":
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
