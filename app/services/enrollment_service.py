"""
Enrollment drive simulation and management.
Plans and tracks enrollment campaigns for high-priority districts.
"""

import pandas as pd
from typing import Dict, List
from datetime import datetime, timedelta
import json
import os


class EnrollmentDriveService:
    """
    Manages enrollment campaigns and simulates outcomes.
    """
    
    @staticmethod
    def plan_enrollment_drive(
        district: str,
        target_households: int,
        priority_level: str,
        estimated_enrollment_rate: float = 0.70
    ) -> Dict:
        """
        Plan an enrollment drive for a district.
        
        Args:
            district (str): Target district
            target_households (int): Number of households to target
            priority_level (str): Priority level (HIGH/MEDIUM/LOW)
            estimated_enrollment_rate (float): Expected enrollment success rate
        
        Returns:
            dict: Enrollment drive plan
        """
        
        # Calculate targets
        expected_enrollments = int(target_households * estimated_enrollment_rate)
        estimated_cost_per_household = 50  # ₹50 per household
        estimated_total_cost = target_households * estimated_cost_per_household
        
        # Calculate impact
        coverage_increase_pct = (expected_enrollments / target_households) * 100
        estimated_lives_covered = expected_enrollments * 5  # 5 family members avg
        
        # Calculate healthcare impact (estimate based on enrollment)
        estimated_claims_per_household = 0.3  # 30% will make claims
        estimated_avg_claim_value = 150000  # ₹1.5L average claim
        estimated_healthcare_expenditure = (
            expected_enrollments * 
            estimated_claims_per_household * 
            estimated_avg_claim_value
        )
        
        return {
            "drive_id": f"DRV{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "district": district,
            "status": "planned",
            "priority_level": priority_level,
            "target_households": target_households,
            "target_enrollments": expected_enrollments,
            "target_lives": estimated_lives_covered,
            "estimated_enrollment_rate_%": estimated_enrollment_rate * 100,
            "estimated_cost_₹": estimated_total_cost,
            "estimated_cost_per_enrollment_₹": estimated_total_cost / expected_enrollments if expected_enrollments > 0 else 0,
            "estimated_lives_covered": estimated_lives_covered,
            "estimated_healthcare_access_increase_%": coverage_increase_pct,
            "estimated_total_healthcare_value_₹": estimated_healthcare_expenditure,
            "planned_date": datetime.utcnow().isoformat(),
            "estimated_duration_days": 30
        }
    
    @staticmethod
    def simulate_enrollment_results(
        enrollment_plan: Dict,
        actual_enrollment_rate: float = None
    ) -> Dict:
        """
        Simulate enrollment drive results.
        
        Args:
            enrollment_plan (dict): Enrollment drive plan
            actual_enrollment_rate (float, optional): Override estimated rate
        
        Returns:
            dict: Simulation results
        """
        
        # Use actual rate or estimate
        rate = actual_enrollment_rate or (enrollment_plan['estimated_enrollment_rate_%'] / 100)
        
        # Simulate results
        actual_enrollments = int(enrollment_plan['target_households'] * rate)
        actual_lives_covered = actual_enrollments * 5
        
        # Cost efficiency
        actual_cost_per_enrollment = (
            enrollment_plan['estimated_cost_₹'] / actual_enrollments 
            if actual_enrollments > 0 else 0
        )
        
        # Health impact
        actual_claims_filed = int(actual_enrollments * 0.3)
        total_claims_value = actual_claims_filed * 150000
        
        return {
            "drive_id": enrollment_plan['drive_id'],
            "district": enrollment_plan['district'],
            "status": "completed",
            "actual_enrollments": actual_enrollments,
            "target_enrollments": enrollment_plan['target_enrollments'],
            "actual_enrollment_rate_%": (actual_enrollments / enrollment_plan['target_households']) * 100,
            "actual_lives_covered": actual_lives_covered,
            "actual_cost_per_enrollment_₹": actual_cost_per_enrollment,
            "claims_filed": actual_claims_filed,
            "total_claims_value_₹": total_claims_value,
            "cost_per_claim_covered_₹": (
                enrollment_plan['estimated_cost_₹'] / actual_claims_filed 
                if actual_claims_filed > 0 else 0
            ),
            "roi_%": (
                (total_claims_value - enrollment_plan['estimated_cost_₹']) / 
                enrollment_plan['estimated_cost_₹'] * 100
            ) if enrollment_plan['estimated_cost_₹'] > 0 else 0,
            "completion_date": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def create_demo_sequence(inclusion_results_df: pd.DataFrame) -> List[Dict]:
        """
        Create a demo-ready enrollment drive sequence.
        Shows the full demo flow in smooth 60 seconds.
        
        Args:
            inclusion_results_df (pd.DataFrame): Inclusion results
        
        Returns:
            list: Demo sequence steps
        """
        
        # Get top priority districts
        unenrolled = inclusion_results_df[inclusion_results_df['status'] == 'unenrolled_eligible']
        top_districts = unenrolled.groupby('district').size().nlargest(3)
        
        demo_sequence = []
        
        for idx, (district, count) in enumerate(top_districts.items()):
            # Plan drive
            plan = EnrollmentDriveService.plan_enrollment_drive(
                district=district,
                target_households=int(count),
                priority_level="HIGH"
            )
            
            # Simulate results (with good outcomes for demo)
            results = EnrollmentDriveService.simulate_enrollment_results(
                plan,
                actual_enrollment_rate=0.75
            )
            
            demo_sequence.append({
                "step": idx + 1,
                "district": district,
                "plan": plan,
                "results": results
            })
        
        return demo_sequence


# Test script
if __name__ == "__main__":
    print("=" * 60)
    print("ENROLLMENT DRIVE SIMULATION")
    print("=" * 60)
    
    # Load inclusion results
    inclusion_df = pd.read_csv("app/data/inclusion_pipeline_results.csv")
    
    # Create demo sequence
    demo_seq = EnrollmentDriveService.create_demo_sequence(inclusion_df)
    
    print(f"\n✓ Created {len(demo_seq)}-step demo sequence\n")
    
    for step in demo_seq:
        print(f"Step {step['step']}: {step['district']}")
        print(f"  Target: {step['plan']['target_households']} households")
        print(f"  Expected enrollments: {step['results']['actual_enrollments']}")
        print(f"  Expected enrollment rate: {step['results']['actual_enrollment_rate_%']:.1f}%")
        print(f"  Lives to be covered: {step['results']['actual_lives_covered']:,}")
        print()