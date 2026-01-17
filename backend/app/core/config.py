# Environment config loader - manages API keys, ports, and app settings from .env

from pydantic_settings import BaseSettings
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
