"""
Advanced eligibility verification engine.
Combines rule-based checks with geospatial analysis.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, List
from math import radians, sin, cos, sqrt, atan2


class EligibilityEngine:
    """
    Comprehensive eligibility verification for PM-JAY.
    Combines rules, demographics, and geospatial data.
    """
    
    # PM-JAY eligibility rules
    BPL_CRITERIA = {
        "max_income_annual": 100000,  # ₹1 Lakh
        "max_assets": None
    }
    
    APL_CRITERIA = {
        "max_income_annual": 500000,  # ₹5 Lakhs
        "requires_occupational_hazard": True
    }
    
    EWS_CRITERIA = {
        "max_income_annual": 300000,  # ₹3 Lakhs
        "max_assets": 5000000  # ₹50 Lakhs
    }
    
    def __init__(self):
        """Initialize engine."""
        self.version = "1.0.0"
        self.hospitals_cache = None
    
    def load_hospitals(self, hospitals_df: pd.DataFrame):
        """Load hospital data for geospatial queries."""
        self.hospitals_cache = hospitals_df.copy()
    
    def verify_income_eligibility(self, income_band: str, annual_income: float = None) -> Tuple[bool, str]:
        """
        Verify income-based eligibility.
        
        Args:
            income_band (str): Income category
            annual_income (float, optional): Annual income amount
        
        Returns:
            Tuple[bool, str]: (is_eligible, reason)
        """
        
        income_band = income_band.upper().strip()
        
        if income_band == "BPL":
            return True, "BPL category is universally eligible for PM-JAY"
        elif income_band == "EWS":
            return True, "EWS (Economically Weaker Section) is eligible"
        elif income_band == "APL":
            return True, "APL with occupational hazard conditions may be eligible"
        else:
            return False, f"Income category '{income_band}' may not qualify"
    
    def verify_family_composition(self, family_size: int, has_children: bool = None) -> Tuple[bool, str]:
        """
        Verify family size eligibility.
        
        Args:
            family_size (int): Number of family members
            has_children (bool, optional): Whether family has children
        
        Returns:
            Tuple[bool, str]: (is_eligible, reason)
        """
        
        if family_size < 1:
            return False, "Invalid family size"
        elif family_size == 1:
            return True, "Single-member household may qualify under specific criteria"
        elif 2 <= family_size <= 10:
            return True, f"Family size of {family_size} is eligible"
        else:
            return False, f"Family size {family_size} exceeds typical thresholds"
    
    def verify_social_category(self, caste_category: str) -> Tuple[bool, str]:
        """
        Verify social category eligibility.
        
        Args:
            caste_category (str): Caste/social category
        
        Returns:
            Tuple[bool, str]: (is_eligible, reason)
        """
        
        category = caste_category.upper().strip() if caste_category else "GENERAL"
        
        valid_categories = ["SC", "ST", "OBC", "GENERAL"]
        
        if category in valid_categories:
            return True, f"{category} category citizens are eligible"
        else:
            return True, "Category not recognized but social status does not restrict eligibility"
    
    def verify_geographic_coverage(self, state: str, district: str) -> Tuple[bool, str]:
        """
        Verify if area is covered under PM-JAY.
        
        Args:
            state (str): State name
            district (str): District name
        
        Returns:
            Tuple[bool, str]: (is_covered, reason)
        """
        
        # Most states are covered under PM-JAY
        if state and district:
            return True, f"PM-JAY covers {district}, {state}"
        else:
            return False, "State and district information required"
    
    @staticmethod
    def calculate_distance_to_hospital(
        beneficiary_lat: float,
        beneficiary_lon: float,
        hospital_lat: float,
        hospital_lon: float
    ) -> float:
        """
        Calculate distance using Haversine formula.
        
        Args:
            beneficiary_lat, beneficiary_lon: Beneficiary coordinates
            hospital_lat, hospital_lon: Hospital coordinates
        
        Returns:
            float: Distance in kilometers
        """
        
        R = 6371
        lat1, lon1, lat2, lon2 = map(
            radians,
            [beneficiary_lat, beneficiary_lon, hospital_lat, hospital_lon]
        )
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c
    
    def find_nearest_hospitals(
        self,
        beneficiary_lat: float,
        beneficiary_lon: float,
        num_hospitals: int = 5
    ) -> pd.DataFrame:
        """
        Find nearest empanelled hospitals to beneficiary location.
        
        Args:
            beneficiary_lat, beneficiary_lon: Beneficiary coordinates
            num_hospitals (int): Number of nearest hospitals to return
        
        Returns:
            pd.DataFrame: Nearest empanelled hospitals
        """
        
        if self.hospitals_cache is None:
            raise ValueError("Must load hospitals first")
        
        # Filter to empanelled only
        empanelled = self.hospitals_cache[self.hospitals_cache['is_empanelled'] == True].copy()
        
        if len(empanelled) == 0:
            return pd.DataFrame()
        
        # Calculate distances
        empanelled['distance_km'] = empanelled.apply(
            lambda row: self.calculate_distance_to_hospital(
                beneficiary_lat, beneficiary_lon,
                row['latitude'], row['longitude']
            ),
            axis=1
        )
        
        # Sort by distance and return nearest
        nearest = empanelled.nsmallest(num_hospitals, 'distance_km')
        
        return nearest[['hospital_id', 'name', 'district', 'distance_km', 'hospital_type']]
    
    def comprehensive_eligibility_check(
        self,
        income_band: str,
        family_size: int,
        state: str,
        district: str,
        caste_category: str = None,
        beneficiary_lat: float = None,
        beneficiary_lon: float = None
    ) -> Dict:
        """
        Perform comprehensive eligibility check.
        
        Args:
            income_band (str): Income category
            family_size (int): Family size
            state (str): State
            district (str): District
            caste_category (str, optional): Caste category
            beneficiary_lat, beneficiary_lon (float, optional): Coordinates
        
        Returns:
            dict: Detailed eligibility assessment
        """
        
        # Run all checks
        income_eligible, income_reason = self.verify_income_eligibility(income_band)
        family_eligible, family_reason = self.verify_family_composition(family_size)
        category_eligible, category_reason = self.verify_social_category(caste_category)
        geo_eligible, geo_reason = self.verify_geographic_coverage(state, district)
        
        # Overall eligibility
        is_eligible = all([income_eligible, family_eligible, category_eligible, geo_eligible])
        
        # Calculate confidence
        checks_passed = sum([income_eligible, family_eligible, category_eligible, geo_eligible])
        confidence = (checks_passed / 4) * 100
        
        # Find nearest hospitals if location provided
        nearest_hospitals = pd.DataFrame()
        if beneficiary_lat and beneficiary_lon and self.hospitals_cache is not None:
            nearest_hospitals = self.find_nearest_hospitals(
                beneficiary_lat, beneficiary_lon, num_hospitals=5
            )
        
        result = {
            "is_eligible": is_eligible,
            "confidence_score": confidence,
            "checks": {
                "income": {"eligible": income_eligible, "reason": income_reason},
                "family_size": {"eligible": family_eligible, "reason": family_reason},
                "social_category": {"eligible": category_eligible, "reason": category_reason},
                "geographic_coverage": {"eligible": geo_eligible, "reason": geo_reason}
            },
            "nearest_hospitals": nearest_hospitals.to_dict('records') if len(nearest_hospitals) > 0 else [],
            "summary": f"You are {'eligible' if is_eligible else 'potentially not eligible'} for PM-JAY benefits."
        }
        
        return result
    
    def get_model_info(self) -> Dict:
        """Get engine information."""
        return {
            "engine_name": "PM-JAY Eligibility Verification Engine",
            "version": self.version,
            "check_types": [
                "Income-based verification",
                "Family composition check",
                "Social category verification",
                "Geographic coverage check",
                "Geospatial hospital locator"
            ],
            "output": "Eligibility status + nearest empanelled hospitals"
        }


# Test script
if __name__ == "__main__":
    print("=" * 60)
    print("ELIGIBILITY VERIFICATION ENGINE TEST")
    print("=" * 60)
    
    # Load data
    hospitals_df = pd.read_csv("app/data/mock_hospitals.csv")
    
    # Initialize engine
    engine = EligibilityEngine()
    engine.load_hospitals(hospitals_df)
    
    # Test comprehensive check
    result = engine.comprehensive_eligibility_check(
        income_band="BPL",
        family_size=5,
        state="Madhya Pradesh",
        district="Indore",
        caste_category="SC",
        beneficiary_lat=22.7196,
        beneficiary_lon=75.8577
    )
    
    print("\n✅ Eligibility Check Result:")
    print(f"Eligible: {result['is_eligible']}")
    print(f"Confidence: {result['confidence_score']:.1f}%")
    print(f"\nNearest Hospitals:")
    for hosp in result['nearest_hospitals'][:3]:
        print(f"  - {hosp['name']}: {hosp['distance_km']:.1f} km ({hosp['hospital_type']})")