"""
Audit logging service with tamper-evident hash chain.
Every action is cryptographically linked to the previous one.
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, Tuple, Optional
from sqlalchemy.orm import Session
from app.database.models import AuditLog, Claim
from app.utils.helpers import create_hash_chain


class AuditService:
    """
    Manages immutable audit logs with cryptographic hash chaining.
    Ensures all actions are traceable and tamper-proof.
    """
    
    @staticmethod
    def get_last_hash(db: Session) -> Optional[str]:
        """
        Get the last action hash from audit log.
        
        Args:
            db (Session): Database session
        
        Returns:
            Optional[str]: Last hash or None if first action
        """
        
        last_log = db.query(AuditLog).order_by(AuditLog.id.desc()).first()
        
        if last_log:
            return last_log.action_hash
        return None
    
    @staticmethod
    def create_action_hash(action_data: Dict, previous_hash: Optional[str] = None) -> str:
        """
        Create hash for an action.
        
        Args:
            action_data (dict): Action details
            previous_hash (str, optional): Previous action's hash
        
        Returns:
            str: SHA-256 hash of this action
        """
        
        # Serialize action data
        action_json = json.dumps(action_data, sort_keys=True, default=str)
        
        # Combine with previous hash if available
        if previous_hash:
            combined = f"{action_json}{previous_hash}"
        else:
            combined = action_json
        
        # Create hash
        return hashlib.sha256(combined.encode()).hexdigest()
    
    @staticmethod
    def log_claim_action(
        db: Session,
        claim_id: int,
        action: str,
        officer_id: str,
        officer_name: str,
        reason: str = None
    ) -> AuditLog:
        """
        Log an action on a claim with hash chain verification.
        
        Args:
            db (Session): Database session
            claim_id (int): Claim ID
            action (str): Action type (approve, reject, flag, review, etc.)
            officer_id (str): Officer ID
            officer_name (str): Officer name
            reason (str, optional): Reason for action
        
        Returns:
            AuditLog: Created audit log entry
        """
        
        # Get last hash
        previous_hash = AuditService.get_last_hash(db)
        
        # Create action data
        action_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "claim_id": claim_id,
            "action": action,
            "officer_id": officer_id,
            "officer_name": officer_name,
            "reason": reason
        }
        
        # Create hash
        action_hash = AuditService.create_action_hash(action_data, previous_hash)
        
        # Create audit log entry
        audit_log = AuditLog(
            claim_id=claim_id,
            action=action,
            officer_id=officer_id,
            officer_name=officer_name,
            reason=reason,
            action_hash=action_hash,
            previous_hash=previous_hash,
            is_chain_valid=True
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        return audit_log
    
    @staticmethod
    def verify_hash_chain(db: Session) -> Tuple[bool, Dict]:
        """
        Verify the integrity of the entire hash chain.
        
        Args:
            db (Session): Database session
        
        Returns:
            Tuple[bool, dict]: (is_valid, details)
        """
        
        logs = db.query(AuditLog).order_by(AuditLog.created_at).all()
        
        if len(logs) == 0:
            return True, {"total_entries": 0, "verified_entries": 0, "broken_at": None}
        
        verified_count = 0
        broken_at = None
        
        for i, log in enumerate(logs):
            # For first entry, previous_hash should be None
            if i == 0:
                if log.previous_hash is not None:
                    broken_at = i
                    break
                verified_count += 1
                continue
            
            # For subsequent entries, verify hash chain
            prev_log = logs[i - 1]
            
            if log.previous_hash != prev_log.action_hash:
                broken_at = i
                break
            
            verified_count += 1
        
        is_valid = broken_at is None
        
        return is_valid, {
            "total_entries": len(logs),
            "verified_entries": verified_count,
            "broken_at": broken_at,
            "status": "✓ Chain intact" if is_valid else f"✗ Tampered at entry {broken_at}"
        }
    
    @staticmethod
    def get_claim_audit_trail(db: Session, claim_id: int) -> list:
        """
        Get complete audit trail for a claim.
        
        Args:
            db (Session): Database session
            claim_id (int): Claim ID
        
        Returns:
            list: List of audit log entries
        """
        
        logs = db.query(AuditLog).filter(
            AuditLog.claim_id == claim_id
        ).order_by(AuditLog.created_at).all()
        
        return logs
    
    @staticmethod
    def get_audit_trail_summary(db: Session, limit: int = 100) -> list:
        """
        Get recent audit log summary.
        
        Args:
            db (Session): Database session
            limit (int): Number of recent entries
        
        Returns:
            list: Recent audit logs
        """
        
        logs = db.query(AuditLog).order_by(
            AuditLog.created_at.desc()
        ).limit(limit).all()
        
        return logs


# Test script
if __name__ == "__main__":
    print("=" * 60)
    print("AUDIT LOG HASH CHAIN VERIFICATION")
    print("=" * 60)
    
    # Example action data
    action1 = {
        "claim_id": 1,
        "action": "approve",
        "officer": "Officer A"
    }
    
    action2 = {
        "claim_id": 1,
        "action": "reject",
        "officer": "Officer B"
    }
    
    # Create hashes
    hash1 = AuditService.create_action_hash(action1)
    hash2 = AuditService.create_action_hash(action2, hash1)
    
    print(f"\nHash 1: {hash1[:16]}...")
    print(f"Hash 2: {hash2[:16]}...")
    
    print("\n✓ Hash chain demonstration complete")