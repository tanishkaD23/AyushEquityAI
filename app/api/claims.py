"""Claim processing endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database.base import get_db
from app.database.models import Claim
from app.models.schemas import ClaimCreate, ClaimResponse, ClaimProcessing
from app.services.claim_service import ClaimService
from typing import Dict

router = APIRouter(prefix="/claims", tags=["claims"])

# Initialize service
claim_service = ClaimService()


@router.post("/submit", response_model=Dict)
async def submit_claim(
    claim: ClaimCreate,
    db: Session = Depends(get_db)
):
    """
    Submit a new healthcare claim.
    Validates schema, scores for fraud, and stores in database.
    
    Args:
        claim (ClaimCreate): Claim information
        db (Session): Database session
    
    Returns:
        dict: Submission acknowledgement with fraud score
    """
    
    claim_dict = claim.dict()
    
    # Process claim
    result = claim_service.process_claim(claim_dict)
    
    # Store in database
    db_claim = Claim(
        claim_id=claim.claim_id,
        beneficiary_id=claim.beneficiary_id,
        hospital_id=claim.hospital_id,
        treatment_code=claim.treatment_code,
        treatment_description=claim.treatment_description,
        billed_amount=claim.billed_amount,
        claim_date=claim.claim_date,
        fraud_score=result['fraud_score'],
        is_flagged=result['is_flagged'],
        flag_reason=result['flag_reason'],
        status=result['status']
    )
    db.add(db_claim)
    db.commit()
    db.refresh(db_claim)
    
    return result


@router.get("/{claim_id}", response_model=ClaimResponse)
async def get_claim(
    claim_id: int,
    db: Session = Depends(get_db)
):
    """
    Get claim details by ID.
    
    Args:
        claim_id (int): Claim ID
        db (Session): Database session
    
    Returns:
        ClaimResponse: Claim details
    """
    
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    return claim


@router.get("/", response_model=List[ClaimResponse])
async def list_claims(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    db: Session = Depends(get_db)
):
    """
    List claims with optional filtering.
    
    Args:
        skip (int): Number to skip
        limit (int): Number to return
        status_filter (str): Filter by status
        db (Session): Database session
    
    Returns:
        List[ClaimResponse]: List of claims
    """
    
    query = db.query(Claim)
    
    if status_filter:
        query = query.filter(Claim.status == status_filter)
    
    claims = query.offset(skip).limit(limit).all()
    return claims