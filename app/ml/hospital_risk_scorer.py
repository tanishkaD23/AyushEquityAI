"""
Hospital Risk Scoring Model.
Combines per-claim fraud scores into hospital-level risk assessment.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
import warnings

warnings.filterwarnings('ignore')


class HospitalRiskScorer:
    """
    Scores hospitals for fraud risk based on claim patterns.
    """
    
    def __init__(self):
        """Initialize scorer."""
        self.version = "1.0.0"
    
    @staticmethod
    def calculate_fraud_risk_score(
        total_claims: int,
        flagged_claims: int,
        avg_claim_amount: float,
        claim_amount_std: float,
        rejection_rate: float,
        avg_distance: float,
        claim_frequency: int
    ) -> Tuple[float, str, Dict]:
        """
        Calculate comprehensive fraud risk score for a hospital.
        
        Args:
            total_claims (int): Total claims from hospital
            flagged_claims (int): Claims flagged as fraud
            avg_claim_amount (float): Average claim amount
            claim_amount_std (float): Std dev of claim amounts
            rejection_rate (float): Rejection rate (%)
            avg_distance (float): Avg distance to beneficiary
            claim_frequency (int): Claim frequency
        
        Returns:
            Tuple[float, str, dict]: Risk score, risk level, details
        """
        
        risk_components = {}
        risk_score = 0.0
        
        # 1. Fraud flag rate (40% weight)
        if total_claims > 0:
            fraud_rate = (flagged_claims / total_claims) * 100
            # Normalize: 0% = 0 points, 20% = 100 points
            fraud_risk = min((fraud_rate / 20) * 100, 100)
            risk_components['fraud_rate'] = fraud_risk
            risk_score += fraud_risk * 0.4
        
        # 2. Claim amount variability (25% weight)
        if avg_claim_amount > 0:
            cv = claim_amount_std / avg_claim_amount  # Coefficient of variation
            # High variability = anomalous = risky
            variability_risk = min(cv * 100, 100)
            risk_components['variability'] = variability_risk
            risk_score += variability_risk * 0.25
        
        # 3. Rejection rate (15% weight)
        # High rejection rate = hospital issues
        rejection_risk = min(rejection_rate * 2, 100)
        risk_components['rejection_rate'] = rejection_risk
        risk_score += rejection_risk * 0.15
        
        # 4. Distance anomaly (10% weight)
        # High average distance = potentially fraudulent claims
        distance_risk = min((avg_distance / 200) * 100, 100)
        risk_components['distance_anomaly'] = distance_risk
        risk_score += distance_risk * 0.1
        
        # 5. Claim volume (10% weight)
        # Very high frequency hospitals may be more risky
        frequency_risk = min((claim_frequency / 500) * 100, 100)
        risk_components['frequency'] = frequency_risk
        risk_score += frequency_risk * 0.1
        
        # Determine risk level
        if risk_score >= 80:
            risk_level = "CRITICAL"
            recommendation = "Suspend empanelment pending investigation"
        elif risk_score >= 60:
            risk_level = "HIGH"
            recommendation = "Enhanced monitoring and claim verification required"
        elif risk_score >= 40:
            risk_level = "MEDIUM"
            recommendation = "Regular monitoring recommended"
        else:
            risk_level = "LOW"
            recommendation = "Normal operations"
        
        return risk_score, risk_level, {
            "components": risk_components,
            "total_claims": total_claims,
            "flagged_claims": flagged_claims,
            "recommendation": recommendation
        }
    
    @staticmethod
    def score_hospitals(
        claims_df: pd.DataFrame,
        hospital_features_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Score all hospitals.
        
        Args:
            claims_df (pd.DataFrame): Claims data
            hospital_features_df (pd.DataFrame): Pre-calculated hospital features
        
        Returns:
            pd.DataFrame: Hospital risk scores
        """
        
        print("🔄 Calculating hospital risk scores...")
        
        scores = []
        
        for _, hospital in hospital_features_df.iterrows():
            # Get flagged claims for this hospital
            hospital_claims = claims_df[claims_df['hospital_id'] == hospital['hospital_id']]
            flagged = (hospital_claims['fraud_pattern'] != 'none').sum()
            
            # Calculate risk score
            risk_score, risk_level, details = HospitalRiskScorer.calculate_fraud_risk_score(
                total_claims=int(hospital['total_claims']),
                flagged_claims=int(flagged),
                avg_claim_amount=float(hospital['avg_claim_amount']),
                claim_amount_std=float(hospital['claim_amount_std']),
                rejection_rate=float(hospital['rejection_rate']),
                avg_distance=float(hospital['avg_patient_distance_km']),
                claim_frequency=int(hospital['total_claims'])
            )
            
            scores.append({
                "hospital_id": hospital['hospital_id'],
                "name": hospital['name'],
                "district": hospital['district'],
                "hospital_type": hospital['hospital_type'],
                "risk_score": risk_score,
                "risk_level": risk_level,
                "total_claims": int(hospital['total_claims']),
                "flagged_claims": flagged,
                "fraud_rate_%": (flagged / hospital['total_claims'] * 100) if hospital['total_claims'] > 0 else 0,
                "avg_claim_amount": hospital['avg_claim_amount'],
                "rejection_rate_%": hospital['rejection_rate'],
                "recommendation": details['recommendation']
            })
        
        df = pd.DataFrame(scores)
        df = df.sort_values('risk_score', ascending=False).reset_index(drop=True)
        df['risk_rank'] = range(1, len(df) + 1)
        
        print(f"✓ Scored {len(df)} hospitals")
        print(f"\nRisk Distribution:")
        print(f"  CRITICAL: {len(df[df['risk_level'] == 'CRITICAL'])}")
        print(f"  HIGH:     {len(df[df['risk_level'] == 'HIGH'])}")
        print(f"  MEDIUM:   {len(df[df['risk_level'] == 'MEDIUM'])}")
        print(f"  LOW:      {len(df[df['risk_level'] == 'LOW'])}")
        
        return df
    
    @staticmethod
    def get_high_risk_hospitals(scores_df: pd.DataFrame, num_top: int = 20) -> pd.DataFrame:
        """Get top high-risk hospitals."""
        return scores_df.head(num_top)
    
    @staticmethod
    def get_district_risk_comparison(scores_df: pd.DataFrame) -> pd.DataFrame:
        """
        Get risk comparison by district.
        
        Args:
            scores_df (pd.DataFrame): Hospital risk scores
        
        Returns:
            pd.DataFrame: District-level risk summary
        """
        
        district_summary = scores_df.groupby('district').agg({
            'risk_score': ['mean', 'max'],
            'hospital_id': 'count',
            'flagged_claims': 'sum'
        }).reset_index()
        
        district_summary.columns = ['district', 'avg_risk_score', 'max_risk_score', 
                                   'num_hospitals', 'total_flagged_claims']
        
        return district_summary.sort_values('avg_risk_score', ascending=False)


# Test script
if __name__ == "__main__":
    print("=" * 60)
    print("HOSPITAL RISK SCORING MODEL")
    print("=" * 60)
    
    # Load data
    claims_df = pd.read_csv("app/data/mock_claims.csv")
    hospital_features_df = pd.read_csv("app/data/hospital_features.csv")
    
    # Score hospitals
    risk_scores = HospitalRiskScorer.score_hospitals(claims_df, hospital_features_df)
    
    # Save
    risk_scores.to_csv("app/data/hospital_risk_scores.csv", index=False)
    print(f"\n✓ Saved: app/data/hospital_risk_scores.csv")
    
    # Show top risk hospitals
    print(f"\n⚠️ Top 10 Highest Risk Hospitals:")
    print(risk_scores.head(10)[['name', 'district', 'risk_score', 'risk_level']].to_string(index=False))
    
    # Show district comparison
    district_risks = HospitalRiskScorer.get_district_risk_comparison(risk_scores)
    print(f"\n📍 District Risk Comparison:")
    print(district_risks.to_string(index=False))