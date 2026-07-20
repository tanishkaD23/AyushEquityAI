"""
Complete Inclusion AI pipeline.
End-to-end: household data → matching → priority score → recommendation.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime
from app.ml.inclusion_matcher import InclusionMatcher
from app.ml.eligibility_scorer import EligibilityScorer


class InclusionAIPipeline:
    """
    End-to-end Inclusion AI pipeline.
    Identifies and prioritizes unenrolled eligible households.
    """
    
    def __init__(self):
        """Initialize pipeline with all components."""
        self.matcher = InclusionMatcher(match_threshold=0.85)
        self.eligibility_scorer = EligibilityScorer()
        self.version = "1.0.0"
        self.enrolled_beneficiaries = None
    
    def load_data(self, beneficiaries_df: pd.DataFrame):
        """Load beneficiary data."""
        self.matcher.load_enrolled_beneficiaries(beneficiaries_df)
        self.enrolled_beneficiaries = beneficiaries_df.copy()
        print(f"✓ Pipeline loaded with {len(beneficiaries_df)} beneficiaries")
    
    def process_household(self, household: Dict) -> Dict:
        """
        Process a single household through the pipeline.
        
        Args:
            household (dict): Household data
        
        Returns:
            dict: Pipeline output with recommendation
        """
        
        # Step 1: Check if already enrolled
        is_match, match_score, match_info = self.matcher.match_household(
            household_name=household.get('name', ''),
            household_aadhaar=household.get('aadhaar_hash'),
            district=household.get('district')
        )
        
        if is_match:
            return {
                "household_id": household.get('household_id'),
                "name": household.get('name'),
                "district": household.get('district'),
                "status": "already_enrolled",
                "matched_beneficiary": match_info.get('beneficiary_id'),
                "confidence": match_score,
                "action": "none"
            }
        
        # Step 2: Eligibility scoring
        is_eligible, eligibility_reason, confidence_score = self.eligibility_scorer.score_beneficiary(
            income_band=household.get('income_band', 'BPL'),
            family_size=household.get('family_size', 5),
            caste_category=household.get('caste_category'),
            district=household.get('district'),
            distance_to_hospital=household.get('distance_to_hospital_km')
        )
        
        if not is_eligible:
            return {
                "household_id": household.get('household_id'),
                "name": household.get('name'),
                "district": household.get('district'),
                "status": "not_eligible",
                "reason": eligibility_reason,
                "confidence": confidence_score,
                "action": "none"
            }
        
        # Step 3: Priority scoring
        # Combine multiple factors
        priority_score = 0.0
        
        # Factor 1: Eligibility score (40%)
        priority_score += confidence_score * 0.4
        
        # Factor 2: Distance to hospital (30%) - higher distance = higher priority
        distance = household.get('distance_to_hospital_km', 20)
        distance_score = min((distance / 100) * 100, 100)
        priority_score += distance_score * 0.3
        
        # Factor 3: Income vulnerability (20%) - lower income = higher priority
        income_band = household.get('income_band', 'BPL')
        if income_band == 'BPL':
            income_score = 100
        elif income_band == 'EWS':
            income_score = 80
        else:
            income_score = 50
        priority_score += income_score * 0.2
        
        # Factor 4: Social category (10%) - SC/ST are higher priority
        caste = household.get('caste_category', 'GENERAL')
        if caste in ['SC', 'ST']:
            caste_score = 100
        elif caste == 'OBC':
            caste_score = 75
        else:
            caste_score = 50
        priority_score += caste_score * 0.1
        
        # Step 4: Generate recommendation
        if priority_score >= 80:
            recommendation = "HIGH_PRIORITY"
            action = "immediate_enrollment"
        elif priority_score >= 60:
            recommendation = "MEDIUM_PRIORITY"
            action = "schedule_enrollment"
        else:
            recommendation = "LOW_PRIORITY"
            action = "monitor"
        
        return {
            "household_id": household.get('household_id'),
            "name": household.get('name'),
            "district": household.get('district'),
            "status": "unenrolled_eligible",
            "recommendation": recommendation,
            "priority_score": priority_score,
            "action": action,
            "eligibility_details": {
                "income_band": household.get('income_band'),
                "family_size": household.get('family_size'),
                "distance_to_hospital_km": distance,
                "caste_category": caste
            },
            "confidence": confidence_score,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def process_district(
        self,
        district_households: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Process all households in a district.
        
        Args:
            district_households (pd.DataFrame): District household data
        
        Returns:
            pd.DataFrame: Pipeline results with rankings
        """
        
        print(f"🔄 Processing {len(district_households)} households...")
        
        results = []
        for idx, row in district_households.iterrows():
            household_dict = row.to_dict()
            result = self.process_household(household_dict)
            results.append(result)
        
        results_df = pd.DataFrame(results)
        
        # Rank by priority
        unenrolled = results_df[results_df['status'] == 'unenrolled_eligible'].copy()
        if len(unenrolled) > 0:
            unenrolled['priority_rank'] = unenrolled['priority_score'].rank(
                method='dense', ascending=False
            )
            results_df = pd.concat([
                results_df[results_df['status'] != 'unenrolled_eligible'],
                unenrolled
            ], ignore_index=True)
        
        print(f"✓ Processed {len(results_df)} households")
        print(f"  - Already enrolled: {len(results_df[results_df['status'] == 'already_enrolled'])}")
        print(f"  - Unenrolled eligible: {len(results_df[results_df['status'] == 'unenrolled_eligible'])}")
        print(f"  - Not eligible: {len(results_df[results_df['status'] == 'not_eligible'])}")
        
        return results_df
    
    def process_all_districts(
        self,
        beneficiaries_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Process households across all districts.
        
        Args:
            beneficiaries_df (pd.DataFrame): All beneficiaries
        
        Returns:
            pd.DataFrame: Complete pipeline results
        """
        
        print("\n" + "=" * 60)
        print("INCLUSION AI PIPELINE - FULL PROCESSING")
        print("=" * 60 + "\n")
        
        self.load_data(beneficiaries_df)
        
        all_results = []
        
        for district in beneficiaries_df['district'].unique():
            print(f"\n📍 Processing district: {district}")
            district_data = beneficiaries_df[beneficiaries_df['district'] == district]
            district_results = self.process_district(district_data)
            all_results.append(district_results)
        
        final_results = pd.concat(all_results, ignore_index=True)
        
        # Create global priority ranking
        unenrolled = final_results[final_results['status'] == 'unenrolled_eligible'].copy()
        if len(unenrolled) > 0:
            unenrolled['global_priority_rank'] = unenrolled['priority_score'].rank(
                method='dense', ascending=False
            )
            final_results = pd.concat([
                final_results[final_results['status'] != 'unenrolled_eligible'],
                unenrolled
            ], ignore_index=True)
        
        print(f"\n" + "=" * 60)
        print(f"✓ PIPELINE COMPLETE")
        print(f"=" * 60)
        print(f"\nGlobal Summary:")
        print(f"  Total processed: {len(final_results)}")
        print(f"  Already enrolled: {len(final_results[final_results['status'] == 'already_enrolled'])}")
        print(f"  Unenrolled eligible: {len(final_results[final_results['status'] == 'unenrolled_eligible'])}")
        print(f"  Not eligible: {len(final_results[final_results['status'] == 'not_eligible'])}")
        
        return final_results
    
    def get_top_priorities(self, results_df: pd.DataFrame, num_top: int = 100) -> pd.DataFrame:
        """
        Get top priority households for enrollment.
        
        Args:
            results_df (pd.DataFrame): Pipeline results
            num_top (int): Number of top priorities
        
        Returns:
            pd.DataFrame: Top priority households
        """
        
        unenrolled = results_df[results_df['status'] == 'unenrolled_eligible'].copy()
        return unenrolled.nlargest(num_top, 'priority_score')
    
    def get_model_info(self) -> Dict:
        """Get pipeline information."""
        return {
            "pipeline_name": "Inclusion AI Pipeline",
            "version": self.version,
            "stages": [
                "Enrollment matching (fuzzy name + Aadhaar)",
                "Eligibility scoring (BPL, family size, distance)",
                "Priority calculation (40% eligibility + 30% distance + 20% income + 10% caste)",
                "Recommendation generation (HIGH/MEDIUM/LOW priority)"
            ],
            "output": "Ranked list of unenrolled eligible households ready for enrollment drives"
        }


# Test script
if __name__ == "__main__":
    print("=" * 60)
    print("INCLUSION AI PIPELINE - FULL TEST")
    print("=" * 60)
    
    # Load data
    beneficiaries_df = pd.read_csv("app/data/mock_beneficiaries.csv")
    
    # Run pipeline
    pipeline = InclusionAIPipeline()
    results = pipeline.process_all_districts(beneficiaries_df)
    
    # Save results
    results.to_csv("app/data/inclusion_pipeline_results.csv", index=False)
    print(f"\n✓ Saved: app/data/inclusion_pipeline_results.csv")
    
    # Show top priorities
    print(f"\n🏆 Top 10 High-Priority Enrollment Candidates:")
    top_10 = pipeline.get_top_priorities(results, num_top=10)
    print(top_10[['name', 'district', 'priority_score', 'recommendation']].to_string(index=False))