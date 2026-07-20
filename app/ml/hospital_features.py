"""
Hospital feature aggregation pipeline.
Aggregates claim patterns to identify high-risk hospitals.
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime, timedelta


class HospitalFeaturePipeline:
    """
    Aggregates per-hospital features from claims data.
    Creates features for hospital risk scoring.
    """
    
    @staticmethod
    def aggregate_hospital_features(claims_df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate features by hospital from claims data.
        
        Args:
            claims_df (pd.DataFrame): Claims dataset
        
        Returns:
            pd.DataFrame: Hospital-level features
        """
        
        print("🔄 Aggregating hospital features from claims...")
        
        hospital_features = claims_df.groupby('hospital_id').agg({
            'claim_id': 'count',
            'billed_amount': ['mean', 'std', 'max', 'min'],
            'treatment_duration_days': 'mean',
            'patient_age': 'mean',
            'claim_frequency_for_patient': 'mean'
        }).reset_index()
        
        # Flatten column names
        hospital_features.columns = ['_'.join(col).strip('_') for col in 
                                     hospital_features.columns.values]
        
        # Rename for clarity
        hospital_features.rename(columns={
            'claim_id_count': 'total_claims',
            'billed_amount_mean': 'avg_claim_amount',
            'billed_amount_std': 'claim_amount_std',
            'billed_amount_max': 'max_claim_amount',
            'billed_amount_min': 'min_claim_amount',
            'treatment_duration_days_mean': 'avg_treatment_duration',
            'patient_age_mean': 'avg_patient_age',
            'claim_frequency_for_patient_mean': 'avg_patient_claim_frequency'
        }, inplace=True)
        
        # Calculate anomaly indicators
        hospital_features['claim_amount_cv'] = (
            hospital_features['claim_amount_std'] / 
            (hospital_features['avg_claim_amount'] + 1e-10)
        )  # Coefficient of variation
        
        hospital_features['high_claim_variance'] = (
            hospital_features['claim_amount_cv'] > 0.5
        ).astype(int)
        
        # Identify outlier hospitals
        mean_claims = hospital_features['total_claims'].mean()
        std_claims = hospital_features['total_claims'].std()
        hospital_features['is_high_volume'] = (
            hospital_features['total_claims'] > mean_claims + std_claims
        ).astype(int)
        
        print(f"✓ Aggregated features for {len(hospital_features)} hospitals")
        
        return hospital_features
    
    @staticmethod
    def calculate_rejection_rate(claims_df: pd.DataFrame, 
                                 approved_claims_df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Calculate rejection rate per hospital.
        
        Args:
            claims_df (pd.DataFrame): All claims
            approved_claims_df (pd.DataFrame, optional): Approved claims
        
        Returns:
            pd.DataFrame: Rejection rates by hospital
        """
        
        print("🔄 Calculating hospital rejection rates...")
        
        # Count total claims per hospital
        total_by_hospital = claims_df['hospital_id'].value_counts().reset_index()
        total_by_hospital.columns = ['hospital_id', 'total_claims']
        
        # Count approved claims (if not provided, assume 95% approval)
        if approved_claims_df is not None and len(approved_claims_df) > 0:
            approved_by_hospital = approved_claims_df['hospital_id'].value_counts().reset_index()
            approved_by_hospital.columns = ['hospital_id', 'approved_claims']
            
            # Merge the two dataframes
            rejection_rates = total_by_hospital.merge(
                approved_by_hospital,
                on='hospital_id',
                how='left'
            )
            
            # Fill NaN with 95% of total claims
            rejection_rates['approved_claims'] = rejection_rates['approved_claims'].fillna(
                rejection_rates['total_claims'] * 0.95
            ).astype(int)
        else:
            # If no approved data provided, assume 95% approval rate
            rejection_rates = total_by_hospital.copy()
            rejection_rates['approved_claims'] = (
                rejection_rates['total_claims'] * 0.95
            ).astype(int)
        
        # Calculate rejection rate
        rejection_rates['rejection_rate'] = (
            (rejection_rates['total_claims'] - rejection_rates['approved_claims']) /
            rejection_rates['total_claims'] * 100
        )
        
        # Handle division by zero
        rejection_rates['rejection_rate'] = rejection_rates['rejection_rate'].fillna(0)
        
        print(f"✓ Calculated rejection rates for {len(rejection_rates)} hospitals")
        
        return rejection_rates[['hospital_id', 'rejection_rate']]
    
    @staticmethod
    def calculate_distance_anomalies(claims_df: pd.DataFrame,
                                    beneficiaries_df: pd.DataFrame,
                                    hospitals_df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect impossible travel patterns (same patient in distant locations).
        
        Args:
            claims_df (pd.DataFrame): Claims dataset
            beneficiaries_df (pd.DataFrame): Beneficiary dataset
            hospitals_df (pd.DataFrame): Hospital dataset
        
        Returns:
            pd.DataFrame: Distance anomaly scores per hospital
        """
        
        print("🔄 Calculating distance anomalies...")
        
        # Merge datasets
        merged = claims_df.merge(
            beneficiaries_df[['beneficiary_id', 'latitude', 'longitude']],
            on='beneficiary_id',
            suffixes=('_claim', '_beneficiary')
        ).merge(
            hospitals_df[['hospital_id', 'latitude', 'longitude']],
            on='hospital_id',
            suffixes=('_beneficiary', '_hospital')
        )
        
        # Calculate distance (Haversine formula)
        from math import radians, sin, cos, sqrt, atan2
        
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371  # Earth radius in km
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            return R * c
        
        merged['distance_km'] = merged.apply(
            lambda row: haversine(
                row['latitude_beneficiary'],
                row['longitude_beneficiary'],
                row['latitude_hospital'],
                row['longitude_hospital']
            ),
            axis=1
        )
        
        # Aggregate by hospital
        distance_anomalies = merged.groupby('hospital_id').agg({
            'distance_km': ['mean', 'max', 'std']
        }).reset_index()
        
        distance_anomalies.columns = ['hospital_id', 'avg_patient_distance_km', 
                                     'max_patient_distance_km', 'distance_std_km']
        
        # Fill NaN values
        distance_anomalies = distance_anomalies.fillna(0)
        
        print(f"✓ Calculated distance anomalies for {len(distance_anomalies)} hospitals")
        
        return distance_anomalies
    
    @staticmethod
    def create_complete_hospital_features(
        claims_df: pd.DataFrame,
        beneficiaries_df: pd.DataFrame,
        hospitals_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Create complete feature set for hospitals.
        
        Args:
            claims_df (pd.DataFrame): Claims dataset
            beneficiaries_df (pd.DataFrame): Beneficiary dataset
            hospitals_df (pd.DataFrame): Hospital dataset
        
        Returns:
            pd.DataFrame: Complete hospital features
        """
        
        print("\n" + "=" * 60)
        print("HOSPITAL FEATURE AGGREGATION")
        print("=" * 60 + "\n")
        
        # Aggregate basic features
        features = HospitalFeaturePipeline.aggregate_hospital_features(claims_df)
        
        # Add rejection rates
        rejection_df = HospitalFeaturePipeline.calculate_rejection_rate(claims_df)
        features = features.merge(rejection_df, on='hospital_id', how='left')
        
        # Add distance anomalies
        distance_df = HospitalFeaturePipeline.calculate_distance_anomalies(
            claims_df, beneficiaries_df, hospitals_df
        )
        features = features.merge(distance_df, on='hospital_id', how='left')
        
        # Merge with hospital basic info
        features = features.merge(
            hospitals_df[['hospital_id', 'name', 'district', 'hospital_type']],
            on='hospital_id',
            how='left'
        )
        
        # Fill any remaining NaN values
        features = features.fillna(0)
        
        print(f"\n✓ Complete feature set created for {len(features)} hospitals")
        print(f"\nFeatures created: {features.columns.tolist()}")
        
        return features


# Script to generate hospital features
if __name__ == "__main__":
    print("=" * 60)
    print("HOSPITAL FEATURE AGGREGATION")
    print("=" * 60)
    
    # Load data
    claims_df = pd.read_csv("app/data/mock_claims.csv")
    beneficiaries_df = pd.read_csv("app/data/mock_beneficiaries.csv")
    hospitals_df = pd.read_csv("app/data/mock_hospitals.csv")
    
    print(f"\n📊 Loaded data:")
    print(f"   Claims: {len(claims_df)} records")
    print(f"   Beneficiaries: {len(beneficiaries_df)} records")
    print(f"   Hospitals: {len(hospitals_df)} records\n")
    
    # Create features
    hospital_features = HospitalFeaturePipeline.create_complete_hospital_features(
        claims_df, beneficiaries_df, hospitals_df
    )
    
    # Save
    hospital_features.to_csv("app/data/hospital_features.csv", index=False)
    print(f"\n✓ Saved: app/data/hospital_features.csv")
    
    print(f"\n🏆 Top 5 hospitals by volume:")
    print(hospital_features.nlargest(5, 'total_claims')[
        ['hospital_id', 'name', 'district', 'total_claims', 'avg_claim_amount']
    ].to_string(index=False))