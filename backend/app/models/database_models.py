"""
Database models for users and encrypted tokens.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base
from cryptography.fernet import Fernet
import os
import base64


# Initialize Fernet cipher
def get_cipher():
    """Get or create Fernet cipher instance."""
    from app.core.config import settings
    key = settings.ENCRYPTION_KEY
    
    if not key:
        # Generate a key (in production, this should be set in .env)
        generated_key = Fernet.generate_key()
        print(f"⚠️  WARNING: ENCRYPTION_KEY not set. Generated new key. Set ENCRYPTION_KEY in .env: {generated_key.decode()}")
        return Fernet(generated_key)
    
    # Strip whitespace from key (in case it was copied with spaces)
    key = key.strip()
    
    # Fernet keys are base64-encoded and should be 44 chars (with padding)
    # If missing padding, add it
    if len(key) == 43:
        key = key + '='
    elif len(key) == 42:
        key = key + '=='
    elif len(key) != 44:
        raise ValueError(f"ENCRYPTION_KEY must be 43-44 characters (base64-encoded 32 bytes). Got {len(key)} characters.")
    
    # Fernet keys from .env are base64-encoded strings
    # Fernet() constructor expects bytes that are base64-encoded
    try:
        # First validate it's valid base64
        try:
            decoded = base64.urlsafe_b64decode(key)
            if len(decoded) != 32:
                raise ValueError(f"After base64 decoding, key must be 32 bytes. Got {len(decoded)} bytes.")
        except Exception as e:
            raise ValueError(f"ENCRYPTION_KEY is not valid base64: {e}")
        
        # Convert string to bytes (Fernet will decode the base64 internally)
        key_bytes = key.encode('utf-8')
        return Fernet(key_bytes)
    except ValueError:
        raise
    except Exception as e:
        print(f"⚠️  Encryption setup error: {e}")
        raise ValueError(f"Invalid ENCRYPTION_KEY. Please set a valid Fernet key in .env: {e}")


# Initialize cipher - lazy initialization
_cipher = None

def get_cipher_instance():
    """Get cipher instance, initializing if needed."""
    global _cipher
    if _cipher is None:
        _cipher = get_cipher()
    return _cipher


class User(Base):
    """User model for GitHub OAuth authentication."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    email = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UserToken(Base):
    """Encrypted storage for user GitHub tokens and repository access."""
    __tablename__ = "user_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    encrypted_token = Column(Text, nullable=False)  # Encrypted GitHub token
    repo_url = Column(String, nullable=False)  # Repository URL the token has access to
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @staticmethod
    def encrypt_token(token: str) -> str:
        """Encrypt a GitHub token before storing."""
        cipher_instance = get_cipher_instance()
        if not cipher_instance:
            raise ValueError("Encryption not initialized. Please set ENCRYPTION_KEY in .env")
        encrypted = cipher_instance.encrypt(token.encode())
        return base64.b64encode(encrypted).decode()

    @staticmethod
    def decrypt_token(encrypted_token: str) -> str:
        """Decrypt a stored GitHub token."""
        cipher_instance = get_cipher_instance()
        if not cipher_instance:
            raise ValueError("Encryption not initialized. Please set ENCRYPTION_KEY in .env")
        try:
            encrypted_bytes = base64.b64decode(encrypted_token.encode())
            decrypted = cipher_instance.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt token: {e}")

    def get_token(self) -> str:
        """Get decrypted token for this record."""
        return self.decrypt_token(self.encrypted_token)


class AnalysisHistory(Base):
    """History of repository analyses."""
    __tablename__ = "analysis_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    repo_url = Column(String, nullable=False, index=True)
    trust_score = Column(Integer, nullable=False)
    total_functions = Column(Integer, nullable=False)
    verified_count = Column(Integer, nullable=False)
    discrepancies_count = Column(Integer, nullable=False)
    analysis_data = Column(Text, nullable=True)  # JSON string of full analysis metadata (renamed from 'metadata' - reserved in SQLAlchemy)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
