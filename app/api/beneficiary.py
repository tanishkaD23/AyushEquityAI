"""Beneficiary endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.base import get_db
from app.database.models import Beneficiary
from app.models.schemas import BeneficiaryResponse, BeneficiaryCreate, BeneficiaryUpdate

router = APIRouter(prefix="/beneficiaries", tags=["beneficiaries"])


@router.get("/", response_model=List[BeneficiaryResponse])
async def list_beneficiaries(
    skip: int = 0,
    limit: int = 100,
    district: str = None,
    db: Session = Depends(get_db)
):
    """
    List all beneficiaries with optional filtering.
    
    Args:
        skip (int): Number of records to skip
        limit (int): Number of records to return
        district (str): Filter by district
        db (Session): Database session
    
    Returns:
        List[BeneficiaryResponse]: List of beneficiaries
    """
    query = db.query(Beneficiary)
    
    if district:
        query = query.filter(Beneficiary.district == district)
    
    beneficiaries = query.offset(skip).limit(limit).all()
    return beneficiaries


@router.get("/{beneficiary_id}", response_model=BeneficiaryResponse)
async def get_beneficiary(
    beneficiary_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific beneficiary by ID.
    
    Args:
        beneficiary_id (int): ID of the beneficiary
        db (Session): Database session
    
    Returns:
        BeneficiaryResponse: Beneficiary details
    
    Raises:
        HTTPException: If beneficiary not found
    """
    beneficiary = db.query(Beneficiary).filter(
        Beneficiary.id == beneficiary_id
    ).first()
    
    if not beneficiary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Beneficiary not found"
        )
    
    return beneficiary


@router.post("/", response_model=BeneficiaryResponse, status_code=status.HTTP_201_CREATED)
async def create_beneficiary(
    beneficiary: BeneficiaryCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new beneficiary.
    
    Args:
        beneficiary (BeneficiaryCreate): Beneficiary data
        db (Session): Database session
    
    Returns:
        BeneficiaryResponse: Created beneficiary
    """
    # Check if beneficiary already exists
    existing = db.query(Beneficiary).filter(
        Beneficiary.beneficiary_id == beneficiary.beneficiary_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Beneficiary with this ID already exists"
        )
    
    db_beneficiary = Beneficiary(**beneficiary.dict())
    db.add(db_beneficiary)
    db.commit()
    db.refresh(db_beneficiary)
    
    return db_beneficiary