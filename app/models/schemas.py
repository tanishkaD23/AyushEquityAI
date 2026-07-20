"""
Pydantic schemas for request/response validation.
Defines API input and output models.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============= Beneficiary Schemas =============

class BeneficiaryBase(BaseModel):
    """Base Beneficiary schema with common fields."""
    beneficiary_id: str
    household_id: str
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    income_band: Optional[str] = None
    caste_category: Optional[str] = None
    family_size: Optional[int] = None
    district: str
    state: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    distance_to_hospital: Optional[float] = None


class BeneficiaryCreate(BeneficiaryBase):
    """Schema for creating a new beneficiary."""
    pass


class BeneficiaryUpdate(BaseModel):
    """Schema for updating beneficiary information."""
    is_enrolled: Optional[bool] = None
    inclusion_score: Optional[float] = None
    equity_score: Optional[float] = None
    priority_rank: Optional[int] = None


class BeneficiaryResponse(BeneficiaryBase):
    """Schema for beneficiary API response."""
    id: int
    is_enrolled: bool
    inclusion_score: Optional[float]
    equity_score: Optional[float]
    priority_rank: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============= Hospital Schemas =============

class HospitalBase(BaseModel):
    """Base Hospital schema with common fields."""
    hospital_id: str
    name: str
    state: str
    district: str
    latitude: float
    longitude: float
    hospital_type: str


class HospitalCreate(HospitalBase):
    """Schema for creating a hospital."""
    pass


class HospitalResponse(HospitalBase):
    """Schema for hospital API response."""
    id: int
    is_empanelled: bool
    fraud_risk_score: Optional[float]
    claim_frequency: int
    average_claim_amount: Optional[float]
    rejection_rate: Optional[float]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============= Claim Schemas =============

class ClaimBase(BaseModel):
    """Base Claim schema with common fields."""
    claim_id: str
    beneficiary_id: int
    hospital_id: int
    treatment_code: str
    treatment_description: str
    billed_amount: float


class ClaimCreate(ClaimBase):
    """Schema for submitting a new claim."""
    claim_date: datetime


class ClaimProcessing(BaseModel):
    """Schema for claim processing result."""
    claim_id: str
    fraud_score: float = Field(..., ge=0, le=100)
    is_flagged: bool
    flag_reason: Optional[str] = None
    status: str


class ClaimResponse(ClaimBase):
    """Schema for claim API response."""
    id: int
    fraud_score: Optional[float]
    is_flagged: bool
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============= Eligibility Schemas =============

class EligibilityCheckRequest(BaseModel):
    """Schema for eligibility check request."""
    beneficiary_id: Optional[int] = None
    household_id: Optional[str] = None
    income_band: str
    family_size: int
    caste_category: Optional[str] = None
    district: str


class EligibilityCheckResponse(BaseModel):
    """Schema for eligibility check response."""
    is_eligible: bool
    eligibility_reason: str
    verification_method: str
    confidence_score: Optional[float] = None


# ============= Health Status Schemas =============

class HealthResponse(BaseModel):
    """Schema for API health check endpoint."""
    status: str = "healthy"
    app_name: str
    app_version: str
    message: str = "AyushEquityAI is running"