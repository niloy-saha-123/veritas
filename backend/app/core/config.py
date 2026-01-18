# Environment config loader - manages API keys, ports, and app settings from .env

from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application Info
    APP_NAME: str = os.getenv("APP_NAME", "Veritas.dev")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    
    # Server Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./veritas.db")
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost:3000,http://localhost:5173"
    ).split(",")
    
    # API Keys for Integrations
    TOKEN_COMPANY_API_KEY: str = os.getenv("TOKEN_COMPANY_API_KEY", "")
    DEVSWARM_API_KEY: str = os.getenv("DEVSWARM_API_KEY", "")
    ARIZE_API_KEY: str = os.getenv("ARIZE_API_KEY", "")
    LEANMCP_API_KEY: str = os.getenv("LEANMCP_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")  # Fallback for non-authenticated users
    
    # GitHub OAuth
    GITHUB_CLIENT_ID: str = os.getenv("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET: str = os.getenv("GITHUB_CLIENT_SECRET", "")
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "")  # For encrypting tokens
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


# Global settings instance
settings = Settings()
