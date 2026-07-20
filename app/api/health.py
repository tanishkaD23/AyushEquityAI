"""Health check endpoint for API."""

from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.config.settings import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        HealthResponse: Status of the API
    """
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        app_version=settings.app_version,
        message="AyushEquityAI API is running"
    )