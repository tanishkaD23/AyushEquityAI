"""
Claim processing service.
Handles claim submission, validation, and fraud scoring.
"""

import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime
from app.ml.fraud_detector import FraudDetector
import os
from sqlalchemy.orm import Session
from app.database.models import Claim


class ClaimService:
    """Service for processing healthcare claims."""
    
    def __init__(self):
        """Initialize claim service."""
        self.fraud_detector = None
        self.load_fraud_model()
        self.claims_cache = []
    
    def load_fraud_model(self):
        """Load trained fraud detection model."""
        model_path = "app/ml/models/fraud_detector.pkl"
        if os.path.exists(model_path):
            self.fraud_detector = FraudDetector.load_model(model_path)
            print("✓ Fraud model loaded")
        else:
            print("⚠ Fraud model not found - training skipped claims will not be scored")
    
    def validate_claim(self, claim_data: Dict) -> Tuple[bool, str]:
        """
        Validate claim data.
        
        Args:
            claim_data (dict): Claim information
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        
        # Check required fields
        required_fields = ['hospital_id', 'beneficiary_id', 'treatment_code', 'billed_amount']
        for field in required_fields:
            if field not in claim_data or not claim_data[field]:
                return False, f"Missing required field: {field}"
        
        # Validate amount
        if claim_data['billed_amount'] < 0:
            return False, "Billed amount cannot be negative"
        
        if claim_data['billed_amount'] > 10000000:  # 1 Crore limit
            return False, "Billed amount exceeds maximum limit"
        
        return True, ""
    
    def score_claim(self, claim_data: Dict) -> Dict:
        """
        Score a claim for fraud risk.
        
        Args:
            claim_data (dict): Claim information
        
        Returns:
            dict: Fraud scoring results
        """
        
        # Default response
        response = {
            "claim_id": claim_data.get("claim_id", ""),
            "fraud_score": 0.0,
            "is_flagged": False,
            "flag_reason": "",
            "confidence": "low"
        }
        
        # If fraud model not loaded, return default
        if not self.fraud_detector or not self.fraud_detector.is_trained:
            return response
        
        try:
            # Prepare features
            features_df = pd.DataFrame([{
                'billed_amount': claim_data.get('billed_amount', 0),
                'treatment_duration_days': claim_data.get('treatment_duration_days', 5),
                'patient_age': claim_data.get('patient_age', 45),
                'claim_frequency_for_hospital': claim_data.get('claim_frequency_for_hospital', 10),
                'claim_frequency_for_patient': claim_data.get('claim_frequency_for_patient', 1),
                'days_since_last_claim': claim_data.get('days_since_last_claim', 30)
            }])
            
            # Get fraud probability
            fraud_scores = self.fraud_detector.predict_proba_fraud(features_df)
            fraud_score = float(fraud_scores[0])
            
            # Flag if score > 70
            is_flagged = fraud_score > 70.0
            flag_reason = "High fraud probability" if is_flagged else ""
            
            response.update({
                "fraud_score": fraud_score,
                "is_flagged": is_flagged,
                "flag_reason": flag_reason,
                "confidence": "high"
            })
            
        except Exception as e:
            print(f"⚠ Error scoring claim: {str(e)}")
        
        return response
    
    def process_claim(self, claim_data: Dict) -> Dict:
        """
        Process a complete claim submission.
        
        Args:
            claim_data (dict): Claim information
        
        Returns:
            dict: Processing result with status and fraud score
        """
        
        # Validate
        is_valid, error = self.validate_claim(claim_data)
        if not is_valid:
            return {
                "status": "rejected",
                "reason": error,
                "fraud_score": 0.0,
                "is_flagged": False
            }
        
        # Score for fraud
        fraud_result = self.score_claim(claim_data)
        
        # Determine status
        if fraud_result['is_flagged']:
            status = "flagged_for_review"
        else:
            status = "approved"
        
        return {
            "claim_id": claim_data.get("claim_id"),
            "status": status,
            "fraud_score": fraud_result['fraud_score'],
            "is_flagged": fraud_result['is_flagged'],
            "flag_reason": fraud_result['flag_reason'],
            "processed_at": datetime.utcnow().isoformat()
        }
def process_claim_with_audit(
    self,
    db: Session,
    claim_data: Dict,
    officer_id: str,
    officer_name: str
) -> Dict:
    """
    Process claim and create audit log entry.
    
    Args:
        db (Session): Database session
        claim_data (dict): Claim information
        officer_id (str): Officer ID
        officer_name (str): Officer name
    
    Returns:
        dict: Processing result with audit log
    """
    
    from app.services.audit_service import AuditService
    
    # Process claim
    result = self.process_claim(claim_data)
    
    # Create audit log
    if 'claim_id' in result:
        claim = db.query(Claim).filter(
            Claim.claim_id == result['claim_id']
        ).first()
        
        if claim:
            audit_log = AuditService.log_claim_action(
                db=db,
                claim_id=claim.id,
                action=result['status'],
                officer_id=officer_id,
                officer_name=officer_name,
                reason=result.get('flag_reason', '')
            )
            
            result['audit_log_id'] = audit_log.id
            result['action_hash'] = audit_log.action_hash
    
    return result    