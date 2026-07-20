"""Admin and officer endpoints for claim processing and monitoring."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from app.database.base import get_db
from app.database.models import AuditLog, Claim
from app.services.claim_service import ClaimService
from app.services.audit_service import AuditService

router = APIRouter(prefix="/admin", tags=["admin"])

claim_service = ClaimService()


@router.get("/audit-log/{claim_id}")
async def get_claim_audit_trail(
    claim_id: int,
    db: Session = Depends(get_db)
):
    """
    Get audit trail for a claim.
    Shows all officer actions and decisions.
    
    Args:
        claim_id (int): Claim ID
        db (Session): Database session
    
    Returns:
        list: Audit trail for the claim
    """
    
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found"
        )
    
    audit_trail = AuditService.get_claim_audit_trail(db, claim_id)
    
    return {
        "claim_id": claim_id,
        "claim_ref": claim.claim_id,
        "audit_entries": [
            {
                "action": log.action,
                "officer_name": log.officer_name,
                "timestamp": log.created_at.isoformat(),
                "reason": log.reason,
                "action_hash": log.action_hash[:16] + "..."
            }
            for log in audit_trail
        ]
    }


@router.get("/verify-chain")
async def verify_audit_chain(db: Session = Depends(get_db)):
    """
    Verify the integrity of the entire audit hash chain.
    
    Args:
        db (Session): Database session
    
    Returns:
        dict: Chain verification status
    """
    
    is_valid, details = AuditService.verify_hash_chain(db)
    
    return {
        "chain_valid": is_valid,
        **details,
        "message": "✓ Chain is tamper-proof" if is_valid else "⚠ Chain has been tampered with"
    }


@router.get("/hospital-risks")
async def get_hospital_risks():
    """
    Get hospital risk scores and rankings.
    
    Returns:
        dict: Hospital risk data
    """
    
    import pandas as pd
    
    try:
        risk_df = pd.read_csv("app/data/hospital_risk_scores.csv")
        
        critical = risk_df[risk_df['risk_level'] == 'CRITICAL'].to_dict('records')
        high = risk_df[risk_df['risk_level'] == 'HIGH'].to_dict('records')
        
        return {
            "total_hospitals": len(risk_df),
            "critical_risk_count": len(critical),
            "high_risk_count": len(high),
            "critical_hospitals": critical[:5],
            "high_risk_hospitals": high[:5]
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk scores not calculated yet"
        )


@router.get("/inclusion-pipeline")
async def get_inclusion_pipeline_results():
    """
    Get inclusion pipeline results and top priorities.
    
    Returns:
        dict: Pipeline results and recommendations
    """
    
    import pandas as pd
    
    try:
        results_df = pd.read_csv("app/data/inclusion_pipeline_results.csv")
        
        unenrolled = results_df[results_df['status'] == 'unenrolled_eligible']
        top_priorities = unenrolled.nlargest(10, 'priority_score').to_dict('records')
        
        return {
            "total_processed": len(results_df),
            "already_enrolled": len(results_df[results_df['status'] == 'already_enrolled']),
            "unenrolled_eligible": len(results_df[results_df['status'] == 'unenrolled_eligible']),
            "not_eligible": len(results_df[results_df['status'] == 'not_eligible']),
            "top_10_priorities": top_priorities
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inclusion pipeline not run yet"
        )