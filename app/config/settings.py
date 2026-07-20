"""
Application configuration settings.
Loads from .env file using environment variables.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Attributes:
        app_name (str): Name of the application
        app_version (str): Version of the application
        debug (bool): Debug mode flag
        fastapi_host (str): FastAPI server host
        fastapi_port (int): FastAPI server port
        fastapi_reload (bool): Reload server on code changes
        database_url (str): SQLite database URL
        database_echo (bool): Log all SQL statements
        streamlit_port (int): Streamlit app port
    """
    
    app_name: str = "AyushEquityAI"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # FastAPI settings
    fastapi_host: str = "127.0.0.1"
    fastapi_port: int = 8000
    fastapi_reload: bool = True
    fastapi_env: str = "development"
    
    # Database settings
    database_url: str = "sqlite:///./app/data/ayushequity.db"
    database_echo: bool = True
    
    # Streamlit settings
    streamlit_port: int = 8501
    streamlit_logger_level: str = "info"
    
    class Config:
        """Pydantic config for Settings."""
        env_file = ".env"
        case_sensitive = False


# Create global settings instance
settings = Settings()