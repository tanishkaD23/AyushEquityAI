"""Main API router that combines all endpoints."""

from fastapi import APIRouter
from app.api import health, beneficiary, eligibility, claims, admin

# Create main router
api_router = APIRouter(prefix="/api/v1")

# Include all sub-routers
api_router.include_router(health.router)
api_router.include_router(beneficiary.router)
api_router.include_router(eligibility.router)
api_router.include_router(claims.router)
api_router.include_router(admin.router)