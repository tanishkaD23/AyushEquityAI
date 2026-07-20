"""
Baseline rule-based eligibility scorer for PM-JAY.
Determines if a beneficiary/household is eligible based on predefined rules.

Rules:
1. Income Band: BPL, APL, EWS, or below poverty line
2. Family Size: For welfare scheme eligibility
3. Caste Category: Some schemes target specific categories
4. Distance to Hospital: Rural accessibility is a factor
"""

from typing import Dict, Optional, Tuple


class EligibilityScorer:
    """
    Rule-based eligibility scorer for PM-JAY beneficiaries.
    
    This is a baseline scorer that will be replaced by ML models later.
    Uses hard-coded rules to determine eligibility.
    """
    
    # Eligibility thresholds
    PM_JAY_ELIGIBLE_INCOME_BANDS = ["BPL", "EWS", "POOR", "APL_VULNERABLE"]
    PRIORITY_DISTRICTS = [
        "Indore", "Bhopal", "Pune", "Mumbai", "Bengaluru",
        "Hyderabad", "Chennai", "Kolkata", "Delhi", "Jaipur"
    ]
    
    # Distance threshold for rural areas (in km)
    CRITICAL_DISTANCE_TO_HOSPITAL = 50  # km
    
    def __init__(self):
        """Initialize the eligibility scorer."""
        self.version = "1.0.0"
        self.model_type = "rule_based_baseline"
    
    def score_beneficiary(
        self,
        income_band: str,
        family_size: int,
        caste_category: Optional[str] = None,
        district: Optional[str] = None,
        distance_to_hospital: Optional[float] = None
    ) -> Tuple[bool, str, float]:
        """
        Score a beneficiary for PM-JAY eligibility.
        
        Args:
            income_band (str): Income category (BPL, APL, EWS, etc.)
            family_size (int): Number of members in household
            caste_category (str, optional): Social category
            district (str, optional): District name
            distance_to_hospital (float, optional): Distance to nearest hospital in km
        
        Returns:
            Tuple containing:
                - is_eligible (bool): Whether beneficiary is eligible
                - reason (str): Explanation of eligibility decision
                - confidence_score (float): 0-100, confidence in the decision
        
        Examples:
            >>> scorer = EligibilityScorer()
            >>> is_eligible, reason, score = scorer.score_beneficiary(
            ...     income_band="BPL",
            ...     family_size=5,
            ...     district="Indore"
            ... )
            >>> print(f"Eligible: {is_eligible}, Score: {score}")
            Eligible: True, Score: 95.0
        """
        
        eligibility_points = 0.0
        max_points = 100.0
        reasons = []
        
        # Rule 1: Income band check (40 points)
        income_eligible, income_reason, income_score = self._check_income(income_band)
        eligibility_points += income_score * 0.4
        if income_eligible:
            reasons.append(f"✓ {income_reason}")
        else:
            reasons.append(f"✗ {income_reason}")
        
        # Rule 2: Family size check (20 points)
        family_eligible, family_reason, family_score = self._check_family_size(family_size)
        eligibility_points += family_score * 0.2
        if family_eligible:
            reasons.append(f"✓ {family_reason}")
        else:
            reasons.append(f"✗ {family_reason}")
        
        # Rule 3: Caste/Social category (20 points)
        caste_eligible, caste_reason, caste_score = self._check_caste_category(caste_category)
        eligibility_points += caste_score * 0.2
        if caste_eligible:
            reasons.append(f"✓ {caste_reason}")
        else:
            reasons.append(f"✗ {caste_reason}")
        
        # Rule 4: Distance to hospital (15 points)
        distance_eligible, distance_reason, distance_score = self._check_distance(distance_to_hospital)
        eligibility_points += distance_score * 0.15
        if distance_eligible:
            reasons.append(f"✓ {distance_reason}")
        else:
            reasons.append(f"✗ {distance_reason}")
        
        # Rule 5: Priority district (5 points)
        district_eligible, district_reason, district_score = self._check_district(district)
        eligibility_points += district_score * 0.05
        if district_eligible:
            reasons.append(f"✓ {district_reason}")
        
        # Final decision
        confidence_score = eligibility_points
        is_eligible = confidence_score >= 60.0  # 60% threshold for eligibility
        
        final_reason = " | ".join(reasons)
        
        return is_eligible, final_reason, confidence_score
    
    def _check_income(self, income_band: str) -> Tuple[bool, str, float]:
        """Check if income band qualifies for PM-JAY."""
        if not income_band:
            return False, "Income band not provided", 0.0
        
        income_band = income_band.upper().strip()
        
        if income_band in self.PM_JAY_ELIGIBLE_INCOME_BANDS:
            return True, f"Income band {income_band} is PM-JAY eligible", 100.0
        elif income_band in ["APL", "MIDDLE_CLASS"]:
            return True, f"Income band {income_band} qualifies under APL-eligible schemes", 70.0
        else:
            return False, f"Income band {income_band} does not qualify", 0.0
    
    def _check_family_size(self, family_size: int) -> Tuple[bool, str, float]:
        """Check if family size qualifies."""
        if family_size <= 0:
            return False, "Invalid family size", 0.0
        elif family_size >= 2:  # Most welfare schemes have family_size >= 2
            return True, f"Family size {family_size} meets minimum requirement", 100.0
        else:
            return False, "Family size below minimum", 0.0
    
    def _check_caste_category(self, caste_category: Optional[str]) -> Tuple[bool, str, float]:
        """Check caste/social category."""
        if not caste_category:
            return True, "No caste-based restrictions apply", 50.0
        
        caste = caste_category.upper().strip()
        
        # All categories are eligible under PM-JAY
        if caste in ["SC", "ST", "OBC", "GENERAL"]:
            return True, f"Caste category {caste} is eligible", 100.0
        else:
            return True, "Caste category not recognized but not restricting eligibility", 75.0
    
    def _check_distance(self, distance_to_hospital: Optional[float]) -> Tuple[bool, str, float]:
        """Check distance to nearest hospital."""
        if distance_to_hospital is None:
            return True, "Distance data unavailable, assuming eligible", 50.0
        
        if distance_to_hospital <= 10:
            return True, f"Close to hospital ({distance_to_hospital:.1f} km)", 100.0
        elif distance_to_hospital <= self.CRITICAL_DISTANCE_TO_HOSPITAL:
            return True, f"Reasonable access to hospital ({distance_to_hospital:.1f} km)", 80.0
        else:
            return True, f"Far from hospital ({distance_to_hospital:.1f} km) - HIGH PRIORITY", 90.0
    
    def _check_district(self, district: Optional[str]) -> Tuple[bool, str, float]:
        """Check if district is a priority area."""
        if not district:
            return True, "District data unavailable", 0.0
        
        if district in self.PRIORITY_DISTRICTS:
            return True, f"Priority district: {district}", 100.0
        else:
            return True, f"Non-priority district: {district}", 0.0
    
    def get_model_info(self) -> Dict[str, str]:
        """Get information about the eligibility scorer."""
        return {
            "model_name": "PM-JAY Eligibility Scorer",
            "version": self.version,
            "type": self.model_type,
            "threshold": "60% confidence score",
            "factors": "income_band, family_size, caste_category, distance_to_hospital, district"
        }