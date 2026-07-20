"""
Main FastAPI application for AyushEquityAI.
Entry point for the backend server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.config.settings import settings
from app.database.base import init_db
from app.api.routes import api_router


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    
    app = FastAPI(
        title=settings.app_name,
        description="AI-powered Healthcare Inclusion & Fraud Detection Platform for PM-JAY",
        version=settings.app_version,
        debug=settings.debug
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins (adjust for production)
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize database
    init_db()
    
    # Include API routes
    app.include_router(api_router)
    
    @app.on_event("startup")
    async def startup():
        """Run on application startup."""
        print(f"✓ {settings.app_name} v{settings.app_version} starting up...")
        print(f"✓ Database: {settings.database_url}")
        print(f"✓ Debug mode: {settings.debug}")
    
    @app.on_event("shutdown")
    async def shutdown():
        """Run on application shutdown."""
        print(f"✓ {settings.app_name} shutting down...")
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=settings.fastapi_reload
    )