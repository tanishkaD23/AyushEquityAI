"""Eligibility check endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.database.models import Beneficiary, EligibilityCheck
from app.models.schemas import EligibilityCheckRequest, EligibilityCheckResponse
from app.ml.eligibility_scorer import EligibilityScorer
from datetime import datetime
from typing import Dict
import pandas as pd

router = APIRouter(prefix="/eligibility", tags=["eligibility"])

# Initialize scorer
eligibility_scorer = EligibilityScorer()
from app.ml.eligibility_engine import EligibilityEngine

# Initialize engine with hospitals
eligibility_engine = EligibilityEngine()

@router.post("/comprehensive-check", response_model=Dict)
async def comprehensive_eligibility_check(
    request: EligibilityCheckRequest,
    db: Session = Depends(get_db)
):
    """
    Comprehensive eligibility check with hospital locator.
    """
    
    # Load hospitals if not already loaded
    if eligibility_engine.hospitals_cache is None:
        hospitals_df = pd.read_csv("app/data/mock_hospitals.csv")
        eligibility_engine.load_hospitals(hospitals_df)
    
    result = eligibility_engine.comprehensive_eligibility_check(
        income_band=request.income_band,
        family_size=request.family_size,
        state="India",  # Default
        district=request.district,
        caste_category=request.caste_category
    )
    
    return result

@router.post("/check", response_model=EligibilityCheckResponse)
async def check_eligibility(
    request: EligibilityCheckRequest,
    db: Session = Depends(get_db)
):
    """
    Check if a beneficiary/household is eligible for PM-JAY.
    
    Args:
        request (EligibilityCheckRequest): Eligibility check parameters
        db (Session): Database session
    
    Returns:
        EligibilityCheckResponse: Eligibility determination and reasoning
    """
    
    # Score the beneficiary
    is_eligible, reason, confidence_score = eligibility_scorer.score_beneficiary(
        income_band=request.income_band,
        family_size=request.family_size,
        caste_category=request.caste_category,
        district=request.district,
        distance_to_hospital=None
    )
    
    # If beneficiary_id provided, log the check
    if request.beneficiary_id:
        beneficiary = db.query(Beneficiary).filter(
            Beneficiary.id == request.beneficiary_id
        ).first()
        
        if beneficiary:
            eligibility_log = EligibilityCheck(
                beneficiary_id=beneficiary.id,
                is_eligible=is_eligible,
                eligibility_reason=reason,
                verification_method="rule_engine",
                check_date=datetime.utcnow()
            )
            db.add(eligibility_log)
            db.commit()
    
    return EligibilityCheckResponse(
        is_eligible=is_eligible,
        eligibility_reason=reason,
        verification_method="rule_engine",
        confidence_score=confidence_score
    )


@router.get("/model-info")
async def get_model_info():
    """
    Get information about the eligibility scorer model.
    
    Returns:
        dict: Model information and configuration
    """
    return eligibility_scorer.get_model_info()