"""
Health Equity Score Model.
Combines multiple factors to create a composite health equity score per village/district.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
import warnings

warnings.filterwarnings('ignore')


class HealthEquityScorer:
    """
    Calculates composite health equity scores at village/district level.
    Combines: enrollment gap, disease burden, distance to facility, doctor availability, fraud risk.
    """
    
    def __init__(self):
        """Initialize equity scorer."""
        self.version = "1.0.0"
        self.district_scores_cache = {}
    
    @staticmethod
    def calculate_enrollment_gap(
        eligible_count: int,
        enrolled_count: int
    ) -> Tuple[float, str]:
        """
        Calculate enrollment gap percentage.
        
        Args:
            eligible_count (int): Total eligible people
            enrolled_count (int): Currently enrolled
        
        Returns:
            Tuple[float, str]: Gap percentage and description
        """
        
        if eligible_count == 0:
            return 0.0, "No eligible population"
        
        gap_pct = ((eligible_count - enrolled_count) / eligible_count) * 100
        
        if gap_pct > 50:
            description = "Critical - More than half unenrolled"
        elif gap_pct > 30:
            description = "High - Significant unenrolled population"
        elif gap_pct > 15:
            description = "Medium - Moderate unenrolled"
        else:
            description = "Low - Well enrolled"
        
        return gap_pct, description
    
    @staticmethod
    def calculate_distance_burden(
        beneficiaries_df: pd.DataFrame,
        district: str
    ) -> Tuple[float, str]:
        """
        Calculate burden of distance to nearest hospital.
        
        Args:
            beneficiaries_df (pd.DataFrame): Beneficiary data
            district (str): District to analyze
        
        Returns:
            Tuple[float, str]: Distance burden score (0-100) and description
        """
        
        district_data = beneficiaries_df[beneficiaries_df['district'] == district]
        
        if len(district_data) == 0:
            return 0.0, "No data available"
        
        # Calculate distance statistics
        avg_distance = district_data['distance_to_hospital_km'].mean()
        pct_remote = (district_data['distance_to_hospital_km'] > 50).sum() / len(district_data) * 100
        
        # Score: higher distance = higher burden = higher score
        if avg_distance > 100:
            burden_score = 100.0
            description = "Critical - Remote area, >100km avg"
        elif avg_distance > 50:
            burden_score = 80.0
            description = "High - Rural area, 50-100km avg"
        elif avg_distance > 20:
            burden_score = 50.0
            description = "Medium - Semi-rural, 20-50km avg"
        else:
            burden_score = 20.0
            description = "Low - Urban area, <20km avg"
        
        return burden_score, description
    
    @staticmethod
    def calculate_fraud_risk_burden(
        fraud_flags_count: int,
        total_claims: int
    ) -> Tuple[float, str]:
        """
        Calculate fraud risk burden for a district.
        
        Args:
            fraud_flags_count (int): Number of flagged claims
            total_claims (int): Total claims in district
        
        Returns:
            Tuple[float, str]: Fraud burden score (0-100)
        """
        
        if total_claims == 0:
            return 0.0, "No claims data"
        
        fraud_rate = (fraud_flags_count / total_claims) * 100
        
        # Convert fraud rate to burden (higher fraud = higher burden on system)
        # Normalize to 0-100
        fraud_burden = min(fraud_rate * 2, 100)
        
        if fraud_rate > 15:
            description = "Critical - High fraud rate affects trust"
        elif fraud_rate > 10:
            description = "High - Significant fraud concerns"
        elif fraud_rate > 5:
            description = "Medium - Moderate fraud concerns"
        else:
            description = "Low - Good compliance"
        
        return fraud_burden, description
    
    @staticmethod
    def calculate_doctor_availability(
        hospitals_df: pd.DataFrame,
        district: str,
        beneficiary_count: int
    ) -> Tuple[float, str]:
        """
        Calculate doctor/facility availability per beneficiary.
        
        Args:
            hospitals_df (pd.DataFrame): Hospital data
            district (str): District
            beneficiary_count (int): Number of beneficiaries
        
        Returns:
            Tuple[float, str]: Availability burden score (0-100)
        """
        
        district_hospitals = hospitals_df[hospitals_df['district'] == district]
        empanelled = district_hospitals[district_hospitals['is_empanelled'] == True]
        
        # Ratio of beneficiaries to empanelled hospitals
        if len(empanelled) == 0:
            return 100.0, "Critical - No empanelled hospitals"
        
        ratio = beneficiary_count / len(empanelled)
        
        # Optimal ratio: 1 hospital per 10,000 beneficiaries
        if ratio > 50000:
            burden_score = 100.0
            description = "Critical - Extreme hospital shortage"
        elif ratio > 20000:
            burden_score = 80.0
            description = "High - Severe shortage"
        elif ratio > 10000:
            burden_score = 50.0
            description = "Medium - Moderate shortage"
        else:
            burden_score = 20.0
            description = "Low - Adequate facilities"
        
        return burden_score, description
    
    def calculate_district_equity_score(
        self,
        district: str,
        beneficiaries_df: pd.DataFrame,
        claims_df: pd.DataFrame,
        hospitals_df: pd.DataFrame
    ) -> Tuple[float, Dict]:
        """
        Calculate composite health equity score for a district.
        
        Args:
            district (str): District name
            beneficiaries_df (pd.DataFrame): Beneficiary data
            claims_df (pd.DataFrame): Claims data
            hospitals_df (pd.DataFrame): Hospital data
        
        Returns:
            Tuple[float, dict]: Equity score (0-100) and detailed breakdown
        """
        
        # Filter data for district
        district_beneficiaries = beneficiaries_df[beneficiaries_df['district'] == district]
        district_claims = claims_df[claims_df['hospital_id'].isin(
            hospitals_df[hospitals_df['district'] == district]['hospital_id']
        )]
        
        total_eligible = len(district_beneficiaries)
        total_enrolled = (district_beneficiaries['is_enrolled'] == True).sum()
        total_claims = len(district_claims)
        fraud_flags = (district_claims['fraud_pattern'] != 'none').sum()
        
        # Calculate component scores
        enrollment_gap, enrollment_desc = self.calculate_enrollment_gap(
            total_eligible, total_enrolled
        )
        
        distance_burden, distance_desc = self.calculate_distance_burden(
            beneficiaries_df, district
        )
        
        fraud_burden, fraud_desc = self.calculate_fraud_risk_burden(
            fraud_flags, total_claims
        )
        
        doctor_burden, doctor_desc = self.calculate_doctor_availability(
            hospitals_df, district, total_eligible
        )
        
        # Disease burden (simulated based on enrollment gap - proxy for underserved)
        disease_burden = enrollment_gap * 0.5  # Half of enrollment gap
        
        # Composite score (inverse - higher = more need)
        # Weights: enrollment(30%) + distance(25%) + fraud(20%) + doctor(15%) + disease(10%)
        equity_score = (
            (enrollment_gap * 0.30) +
            (distance_burden * 0.25) +
            (fraud_burden * 0.20) +
            (doctor_burden * 0.15) +
            (disease_burden * 0.10)
        )
        
        # Rank: 0-30 (Low need), 30-60 (Medium need), 60-80 (High need), 80-100 (Critical need)
        breakdown = {
            "enrollment_gap_pct": enrollment_gap,
            "enrollment_description": enrollment_desc,
            "distance_burden": distance_burden,
            "distance_description": distance_desc,
            "fraud_burden": fraud_burden,
            "fraud_description": fraud_desc,
            "doctor_availability_burden": doctor_burden,
            "doctor_description": doctor_desc,
            "disease_burden": disease_burden,
            "total_eligible": total_eligible,
            "total_enrolled": total_enrolled,
            "total_claims": total_claims,
            "fraud_flags": fraud_flags
        }
        
        return equity_score, breakdown
    
    def calculate_all_districts(
        self,
        beneficiaries_df: pd.DataFrame,
        claims_df: pd.DataFrame,
        hospitals_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate equity scores for all districts.
        
        Args:
            beneficiaries_df (pd.DataFrame): Beneficiary data
            claims_df (pd.DataFrame): Claims data
            hospitals_df (pd.DataFrame): Hospital data
        
        Returns:
            pd.DataFrame: Equity scores by district
        """
        
        print("🔄 Calculating health equity scores for all districts...")
        
        scores = []
        
        for district in beneficiaries_df['district'].unique():
            score, breakdown = self.calculate_district_equity_score(
                district, beneficiaries_df, claims_df, hospitals_df
            )
            
            scores.append({
                "district": district,
                "equity_score": score,
                **breakdown
            })
        
        df = pd.DataFrame(scores)
        df = df.sort_values('equity_score', ascending=False).reset_index(drop=True)
        df['priority_rank'] = range(1, len(df) + 1)
        
        print(f"✓ Calculated equity scores for {len(df)} districts")
        
        return df
    
    def get_model_info(self) -> Dict:
        """Get model information."""
        return {
            "model_name": "Health Equity Score",
            "version": self.version,
            "components": [
                "Enrollment gap (30%)",
                "Distance to hospitals (25%)",
                "Fraud risk burden (20%)",
                "Doctor availability (15%)",
                "Disease burden (10%)"
            ],
            "scale": "0-100 (0=low need, 100=critical need)",
            "output": "District-level priority ranking"
        }


# Script to calculate equity scores
if __name__ == "__main__":
    print("=" * 60)
    print("HEALTH EQUITY SCORE CALCULATION")
    print("=" * 60)
    
    # Load data
    beneficiaries_df = pd.read_csv("app/data/mock_beneficiaries.csv")
    claims_df = pd.read_csv("app/data/mock_claims.csv")
    hospitals_df = pd.read_csv("app/data/mock_hospitals.csv")
    
    # Calculate scores
    scorer = HealthEquityScorer()
    equity_df = scorer.calculate_all_districts(beneficiaries_df, claims_df, hospitals_df)
    
    # Save
    equity_df.to_csv("app/data/district_equity_scores.csv", index=False)
    print(f"\n✓ Saved: app/data/district_equity_scores.csv")
    
    print(f"\n🏆 Top 5 Districts by Health Equity Need:")
    print(equity_df[['district', 'equity_score', 'enrollment_gap_pct', 'priority_rank']].head())