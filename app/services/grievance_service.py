"""
Grievance reporting and classification service.
Handles citizen fraud/grievance reports with text classification.
"""

import pandas as pd
from typing import Dict, Tuple
from datetime import datetime
import json
import os


class GrievanceClassifier:
    """
    Classifies citizen-submitted grievances by type and urgency.
    """
    
    # Grievance types and keywords
    GRIEVANCE_TYPES = {
        "fraud_claim": {
            "keywords": ["duplicate", "fake", "fabricated", "fraudulent", "overbilling", "false claim"],
            "urgency": "high"
        },
        "hospital_misconduct": {
            "keywords": ["denied", "refused", "misbehaved", "discriminated", "negligence", "bad behavior"],
            "urgency": "high"
        },
        "enrollment_issue": {
            "keywords": ["enrolled", "rejected", "denied enrollment", "not eligible", "removed"],
            "urgency": "medium"
        },
        "coverage_denial": {
            "keywords": ["claim rejected", "not covered", "denied coverage", "treatment cost"],
            "urgency": "high"
        },
        "documentation": {
            "keywords": ["documents", "aadhaar", "id", "proof", "certificate", "missing"],
            "urgency": "low"
        },
        "other": {
            "keywords": [],
            "urgency": "low"
        }
    }
    
    # Routing departments
    ROUTING_DEPARTMENTS = {
        "fraud_claim": "Fraud Investigation Unit",
        "hospital_misconduct": "Hospital Oversight Board",
        "enrollment_issue": "Enrollment & Grievance Cell",
        "coverage_denial": "Medical Review Board",
        "documentation": "Document Verification Cell",
        "other": "General Grievances Cell"
    }
    
    @staticmethod
    def classify_grievance(grievance_text: str) -> Dict:
        """
        Classify a grievance text.
        
        Args:
            grievance_text (str): Citizen's grievance text
        
        Returns:
            dict: Classification result
        """
        
        text_lower = grievance_text.lower()
        
        # Find matching category
        best_match = "other"
        max_keywords_found = 0
        
        for grievance_type, info in GrievanceClassifier.GRIEVANCE_TYPES.items():
            keywords_found = sum(1 for kw in info['keywords'] if kw in text_lower)
            
            if keywords_found > max_keywords_found:
                max_keywords_found = keywords_found
                best_match = grievance_type
        
        grievance_type = best_match
        urgency = GrievanceClassifier.GRIEVANCE_TYPES[grievance_type]['urgency']
        routing_dept = GrievanceClassifier.ROUTING_DEPARTMENTS[grievance_type]
        
        # Calculate confidence
        if max_keywords_found > 0:
            confidence = min(0.5 + (max_keywords_found * 0.25), 1.0)
        else:
            confidence = 0.5
        
        return {
            "grievance_type": grievance_type,
            "urgency_level": urgency,
            "routing_department": routing_dept,
            "confidence": confidence,
            "keywords_found": max_keywords_found,
            "classified_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def get_urgency_priority(urgency_level: str) -> int:
        """Get numeric priority for sorting."""
        priority_map = {"high": 1, "medium": 2, "low": 3}
        return priority_map.get(urgency_level, 999)


class GrievanceService:
    """
    Service for handling citizen grievances.
    """
    
    def __init__(self):
        """Initialize grievance service."""
        self.grievances = []
    
    def submit_grievance(
        self,
        beneficiary_id: str,
        grievance_text: str,
        contact_phone: str = None,
        grievance_id: str = None
    ) -> Dict:
        """
        Submit a new grievance.
        
        Args:
            beneficiary_id (str): Beneficiary ID
            grievance_text (str): Grievance description
            contact_phone (str, optional): Contact phone number
            grievance_id (str, optional): Grievance reference ID
        
        Returns:
            dict: Submission confirmation
        """
        
        # Generate grievance ID if not provided
        if not grievance_id:
            grievance_id = f"GRV{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Classify grievance
        classification = GrievanceClassifier.classify_grievance(grievance_text)
        
        # Create grievance record
        grievance = {
            "grievance_id": grievance_id,
            "beneficiary_id": beneficiary_id,
            "grievance_text": grievance_text,
            "contact_phone": contact_phone,
            "submitted_at": datetime.utcnow().isoformat(),
            "status": "submitted",
            **classification
        }
        
        self.grievances.append(grievance)
        
        return {
            "grievance_id": grievance_id,
            "status": "received",
            "grievance_type": classification['grievance_type'],
            "urgency_level": classification['urgency_level'],
            "routing_department": classification['routing_department'],
            "message": f"Grievance received and routed to {classification['routing_department']}. Reference ID: {grievance_id}"
        }
    
    def get_pending_grievances(self) -> list:
        """Get all pending grievances."""
        return [g for g in self.grievances if g['status'] == 'submitted']
    
    def get_grievances_by_urgency(self) -> Dict:
        """Get grievances grouped by urgency."""
        grouped = {"high": [], "medium": [], "low": []}
        
        for grievance in self.get_pending_grievances():
            urgency = grievance['urgency_level']
            if urgency in grouped:
                grouped[urgency].append(grievance)
        
        return grouped
    
    def export_grievances(self, filepath: str = "app/data/grievances.json"):
        """Export grievances to file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.grievances, f, indent=2)
        
        print(f"✓ Exported {len(self.grievances)} grievances to {filepath}")


# Test script
if __name__ == "__main__":
    print("=" * 60)
    print("GRIEVANCE CLASSIFICATION & ROUTING TEST")
    print("=" * 60)
    
    service = GrievanceService()
    
    # Test cases
    test_grievances = [
        "The hospital submitted a duplicate claim for my treatment. They billed me twice for the same surgery!",
        "The hospital staff refused to treat me because of my caste. They discriminated against me.",
        "My enrollment application was rejected without proper reason. I am eligible but they denied it.",
        "The treatment was expensive and they denied my claim coverage. Why?"
    ]
    
    print("\n📝 Processing test grievances...\n")
    
    for text in test_grievances:
        result = service.submit_grievance(
            beneficiary_id="BEN000001",
            grievance_text=text
        )
        print(f"Text: {text[:50]}...")
        print(f"Type: {result['grievance_type']}")
        print(f"Urgency: {result['urgency_level']}")
        print(f"Route: {result['routing_department']}")
        print()
    
    print(f"✓ Processed {len(service.grievances)} grievances")