"""
District-level analytics aggregating inclusion, fraud, and equity metrics.
"""

import pandas as pd
import numpy as np
from typing import Dict
from scipy import stats
import warnings

warnings.filterwarnings('ignore')


class DistrictAnalytics:
    """
    Comprehensive district-level analytics for PM-JAY.
    Combines inclusion, fraud, and equity dimensions.
    """
    
    @staticmethod
    def calculate_inclusion_analytics(
        inclusion_results_df: pd.DataFrame
    ) -> Dict:
        """
        Calculate district-level inclusion metrics.
        
        Args:
            inclusion_results_df (pd.DataFrame): Inclusion pipeline results
        
        Returns:
            dict: District inclusion analytics
        """
        
        print("🔄 Calculating inclusion analytics...")
        
        analytics = {}
        
        for district in inclusion_results_df['district'].unique():
            district_data = inclusion_results_df[
                inclusion_results_df['district'] == district
            ]
            
            unenrolled_eligible = district_data[
                district_data['status'] == 'unenrolled_eligible'
            ]
            
            analytics[district] = {
                "total_processed": len(district_data),
                "already_enrolled": len(district_data[district_data['status'] == 'already_enrolled']),
                "unenrolled_eligible": len(unenrolled_eligible),
                "not_eligible": len(district_data[district_data['status'] == 'not_eligible']),
                "avg_priority_score": unenrolled_eligible['priority_score'].mean() if len(unenrolled_eligible) > 0 else 0,
                "high_priority_count": len(unenrolled_eligible[unenrolled_eligible['recommendation'] == 'HIGH_PRIORITY'])
            }
        
        return analytics
    
    @staticmethod
    def calculate_fraud_analytics(
        hospital_risk_df: pd.DataFrame
    ) -> Dict:
        """
        Calculate district-level fraud prevention metrics.
        
        Args:
            hospital_risk_df (pd.DataFrame): Hospital risk scores
        
        Returns:
            dict: District fraud analytics
        """
        
        print("🔄 Calculating fraud analytics...")
        
        analytics = {}
        
        for district in hospital_risk_df['district'].unique():
            district_hospitals = hospital_risk_df[
                hospital_risk_df['district'] == district
            ]
            
            analytics[district] = {
                "total_hospitals": len(district_hospitals),
                "critical_risk_count": len(district_hospitals[district_hospitals['risk_level'] == 'CRITICAL']),
                "high_risk_count": len(district_hospitals[district_hospitals['risk_level'] == 'HIGH']),
                "avg_risk_score": district_hospitals['risk_score'].mean(),
                "total_flagged_claims": district_hospitals['flagged_claims'].sum(),
                "avg_fraud_rate_%": district_hospitals['fraud_rate_%'].mean(),
                "estimated_blocked_amount_₹": district_hospitals['flagged_claims'].sum() * 75000  # Avg fraud claim
            }
        
        return analytics
    
    @staticmethod
    def calculate_equity_analytics(
        equity_scores_df: pd.DataFrame
    ) -> Dict:
        """
        Calculate district-level equity metrics.
        
        Args:
            equity_scores_df (pd.DataFrame): Equity scores by district
        
        Returns:
            dict: District equity analytics
        """
        
        print("🔄 Calculating equity analytics...")
        
        analytics = {}
        
        for _, row in equity_scores_df.iterrows():
            district = row['district']
            analytics[district] = {
                "equity_score": row['equity_score'],
                "priority_rank": row['priority_rank'],
                "enrollment_gap_%": row['enrollment_gap_pct'],
                "distance_burden": row['distance_burden'],
                "fraud_burden": row['fraud_burden'],
                "doctor_availability_burden": row['doctor_availability_burden'],
                "total_eligible": row['total_eligible'],
                "total_enrolled": row['total_enrolled']
            }
        
        return analytics
    
    @staticmethod
    def detect_exclusion_patterns(
        beneficiaries_df: pd.DataFrame,
        inclusion_results_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Detect systemic exclusion patterns using chi-square tests.
        
        Args:
            beneficiaries_df (pd.DataFrame): All beneficiaries
            inclusion_results_df (pd.DataFrame): Inclusion pipeline results
        
        Returns:
            pd.DataFrame: Exclusion pattern analysis
        """
        
        print("🔄 Detecting exclusion patterns...")
        
        patterns = []
        
        # Merge for analysis
        merged = beneficiaries_df.merge(
            inclusion_results_df[['household_id', 'status']],
            left_on='household_id',
            right_on='household_id',
            how='left'
        )
        
        # Chi-square test for caste category
        contingency_caste = pd.crosstab(
            merged['caste_category'],
            merged['status'] == 'unenrolled_eligible'
        )
        
        if len(contingency_caste) > 1:
            chi2, p_val, dof, expected = stats.chi2_contingency(contingency_caste)
            
            if p_val < 0.05:  # 95% confidence
                patterns.append({
                    "dimension": "caste_category",
                    "chi_square": chi2,
                    "p_value": p_val,
                    "is_significant": True,
                    "message": "Significant exclusion pattern detected by caste category"
                })
        
        # Chi-square test for income band
        contingency_income = pd.crosstab(
            merged['income_band'],
            merged['status'] == 'unenrolled_eligible'
        )
        
        if len(contingency_income) > 1:
            chi2, p_val, dof, expected = stats.chi2_contingency(contingency_income)
            
            if p_val < 0.05:
                patterns.append({
                    "dimension": "income_band",
                    "chi_square": chi2,
                    "p_value": p_val,
                    "is_significant": True,
                    "message": "Significant exclusion pattern detected by income band"
                })
        
        # Chi-square test for gender
        contingency_gender = pd.crosstab(
            merged['gender'],
            merged['status'] == 'unenrolled_eligible'
        )
        
        if len(contingency_gender) > 1:
            chi2, p_val, dof, expected = stats.chi2_contingency(contingency_gender)
            
            if p_val < 0.05:
                patterns.append({
                    "dimension": "gender",
                    "chi_square": chi2,
                    "p_value": p_val,
                    "is_significant": True,
                    "message": "Significant exclusion pattern detected by gender"
                })
        
        df = pd.DataFrame(patterns)
        print(f"✓ Detected {len(patterns)} significant exclusion patterns")
        
        return df
    
    @staticmethod
    def create_district_report(
        beneficiaries_df: pd.DataFrame,
        inclusion_results_df: pd.DataFrame,
        hospital_risk_df: pd.DataFrame,
        equity_scores_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Create comprehensive district report.
        
        Args:
            beneficiaries_df (pd.DataFrame): Beneficiary data
            inclusion_results_df (pd.DataFrame): Inclusion results
            hospital_risk_df (pd.DataFrame): Hospital risk scores
            equity_scores_df (pd.DataFrame): Equity scores
        
        Returns:
            pd.DataFrame: Complete district report
        """
        
        print("\n" + "=" * 60)
        print("DISTRICT ANALYTICS REPORT")
        print("=" * 60 + "\n")
        
        # Calculate analytics
        inclusion_data = DistrictAnalytics.calculate_inclusion_analytics(inclusion_results_df)
        fraud_data = DistrictAnalytics.calculate_fraud_analytics(hospital_risk_df)
        equity_data = DistrictAnalytics.calculate_equity_analytics(equity_scores_df)
        
        # Combine into single report
        report_rows = []
        
        for district in inclusion_data.keys():
            report_rows.append({
                "district": district,
                
                # Inclusion metrics
                "total_processed": inclusion_data[district]["total_processed"],
                "already_enrolled": inclusion_data[district]["already_enrolled"],
                "unenrolled_eligible": inclusion_data[district]["unenrolled_eligible"],
                "high_priority_targets": inclusion_data[district]["high_priority_count"],
                
                # Fraud metrics
                "total_hospitals": fraud_data.get(district, {}).get("total_hospitals", 0),
                "high_risk_hospitals": fraud_data.get(district, {}).get("high_risk_count", 0) +
                                      fraud_data.get(district, {}).get("critical_risk_count", 0),
                "avg_fraud_rate_%": fraud_data.get(district, {}).get("avg_fraud_rate_%", 0),
                "estimated_savings_₹": fraud_data.get(district, {}).get("estimated_blocked_amount_₹", 0),
                
                # Equity metrics
                "equity_score": equity_data.get(district, {}).get("equity_score", 0),
                "enrollment_gap_%": equity_data.get(district, {}).get("enrollment_gap_%", 0),
                "priority_rank": equity_data.get(district, {}).get("priority_rank", 999)
            })
        
        df = pd.DataFrame(report_rows)
        df = df.sort_values('equity_score', ascending=False).reset_index(drop=True)
        
        print(f"✓ Created comprehensive report for {len(df)} districts")
        
        return df


# Test script
if __name__ == "__main__":
    print("=" * 60)
    print("DISTRICT ANALYTICS")
    print("=" * 60)
    
    # Load data
    beneficiaries_df = pd.read_csv("app/data/mock_beneficiaries.csv")
    inclusion_df = pd.read_csv("app/data/inclusion_pipeline_results.csv")
    hospital_risk_df = pd.read_csv("app/data/hospital_risk_scores.csv")
    equity_df = pd.read_csv("app/data/district_equity_scores.csv")
    
    # Create report
    analytics = DistrictAnalytics()
    report = analytics.create_district_report(beneficiaries_df, inclusion_df, hospital_risk_df, equity_df)
    
    # Save
    report.to_csv("app/data/district_analytics_report.csv", index=False)
    print(f"\n✓ Saved: app/data/district_analytics_report.csv")
    
    # Show report
    print(f"\n📊 District Analytics Summary:")
    print(report[['district', 'equity_score', 'unenrolled_eligible', 'estimated_savings_₹']].head(10).to_string(index=False))
    
    # Detect exclusion patterns
    print(f"\n🔍 Detecting exclusion patterns...")
    exclusions = analytics.detect_exclusion_patterns(beneficiaries_df, inclusion_df)
    if len(exclusions) > 0:
        print(f"Found {len(exclusions)} significant patterns:")
        print(exclusions.to_string(index=False))
    else:
        print("No significant exclusion patterns detected")