"""
Synthetic data generator for PM-JAY claims and beneficiaries.
Generates realistic mock data for testing and development.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os


class DataGenerator:
    """Generate synthetic PM-JAY claims and beneficiary data."""
    
    # Constants for data generation
    DISTRICTS = [
        "Indore", "Bhopal", "Pune", "Mumbai", "Bengaluru",
        "Hyderabad", "Chennai", "Kolkata", "Delhi", "Jaipur",
        "Lucknow", "Ahmedabad", "Chandigarh", "Surat", "Goa"
    ]
    
    STATES = {
        "Indore": "Madhya Pradesh", "Bhopal": "Madhya Pradesh",
        "Pune": "Maharashtra", "Mumbai": "Maharashtra",
        "Bengaluru": "Karnataka", "Hyderabad": "Telangana",
        "Chennai": "Tamil Nadu", "Kolkata": "West Bengal",
        "Delhi": "Delhi", "Jaipur": "Rajasthan",
        "Lucknow": "Uttar Pradesh", "Ahmedabad": "Gujarat",
        "Chandigarh": "Chandigarh", "Surat": "Gujarat", "Goa": "Goa"
    }
    
    INCOME_BANDS = ["BPL", "APL", "EWS"]
    CASTE_CATEGORIES = ["SC", "ST", "OBC", "General"]
    TREATMENT_CODES = [
        "101", "102", "201", "202", "301", "302", "401", "402",
        "501", "502", "601", "602", "701", "702", "801", "802"
    ]
    TREATMENT_NAMES = {
        "101": "Normal Delivery", "102": "Cesarean Delivery",
        "201": "Acute Myocardial Infarction (Heart Attack)", "202": "Unstable Angina",
        "301": "Severe Pneumonia", "302": "Acute Respiratory Distress",
        "401": "Acute Appendicitis", "402": "Emergency Laparotomy",
        "501": "Moderate Head Injury", "502": "Severe Head Injury",
        "601": "Type 2 Diabetes Mellitus", "602": "Diabetic Ketoacidosis",
        "701": "Hypertension Management", "702": "Hypertensive Crisis",
        "801": "Total Knee Replacement", "802": "Hip Joint Replacement"
    }
    
    HOSPITAL_TYPES = ["Government", "Private", "NGO"]
    
    @staticmethod
    def generate_claims_data(num_claims: int = 10000) -> pd.DataFrame:
        """
        Generate synthetic PM-JAY claims dataset.
        
        Args:
            num_claims (int): Number of claims to generate
        
        Returns:
            pd.DataFrame: Claims dataset
        """
        
        print(f"🔄 Generating {num_claims} synthetic claims...")
        
        claims = []
        
        # Create base hospitals
        num_hospitals = 150
        hospitals = [f"HOS{i:04d}" for i in range(1, num_hospitals + 1)]
        
        # Create beneficiaries
        num_beneficiaries = 5000
        beneficiaries = [f"BEN{i:06d}" for i in range(1, num_beneficiaries + 1)]
        
        # Generate claims with fraud patterns
        for i in range(num_claims):
            claim_id = f"CLM{i:08d}"
            
            # Select hospital and beneficiary
            hospital_id = random.choice(hospitals)
            beneficiary_id = random.choice(beneficiaries)
            
            # Treatment details
            treatment_code = random.choice(DataGenerator.TREATMENT_CODES)
            treatment_name = DataGenerator.TREATMENT_NAMES.get(treatment_code, "Unknown")
            
            # Claim amount (with fraud patterns)
            base_amount = random.randint(10000, 500000)
            
            # Inject fraud patterns
            fraud_pattern = random.random()
            
            if fraud_pattern < 0.05:  # 5% fraud rate
                # Pattern 1: Overbilling (20-50% higher than normal)
                billed_amount = int(base_amount * random.uniform(1.2, 1.5))
                fraud_indicator = "overbilling"
            elif fraud_pattern < 0.08:  # 3% fraud rate
                # Pattern 2: Duplicate claims (same patient, same treatment, within 7 days)
                billed_amount = base_amount
                fraud_indicator = "duplicate"
            elif fraud_pattern < 0.10:  # 2% fraud rate
                # Pattern 3: Impossible travel (patient in 2 cities same day)
                billed_amount = base_amount
                fraud_indicator = "impossible_travel"
            else:
                billed_amount = base_amount
                fraud_indicator = "none"
            
            # Date range (past 6 months)
            days_back = random.randint(0, 180)
            claim_date = datetime.now() - timedelta(days=days_back)
            
            claims.append({
                "claim_id": claim_id,
                "hospital_id": hospital_id,
                "beneficiary_id": beneficiary_id,
                "treatment_code": treatment_code,
                "treatment_name": treatment_name,
                "claim_date": claim_date,
                "billed_amount": billed_amount,
                "treatment_duration_days": random.randint(1, 30),
                "patient_age": random.randint(18, 85),
                "patient_gender": random.choice(["M", "F"]),
                "claim_frequency_for_hospital": random.randint(1, 50),
                "claim_frequency_for_patient": random.randint(1, 10),
                "days_since_last_claim": random.randint(0, 365),
                "fraud_pattern": fraud_indicator,
                "status": "submitted"
            })
        
        df = pd.DataFrame(claims)
        
        print(f"✓ Generated {num_claims} claims")
        print(f"✓ Fraud rate: {(df['fraud_pattern'] != 'none').sum() / len(df) * 100:.2f}%")
        
        return df
    
    @staticmethod
    def generate_beneficiary_data(num_beneficiaries: int = 5000) -> pd.DataFrame:
        """
        Generate synthetic beneficiary/household dataset.
        
        Args:
            num_beneficiaries (int): Number of beneficiaries to generate
        
        Returns:
            pd.DataFrame: Beneficiary dataset
        """
        
        print(f"🔄 Generating {num_beneficiaries} synthetic beneficiaries...")
        
        beneficiaries = []
        
        for i in range(num_beneficiaries):
            beneficiary_id = f"BEN{i:06d}"
            household_id = f"HH{i:06d}"
            
            district = random.choice(DataGenerator.DISTRICTS)
            state = DataGenerator.STATES[district]
            
            # Demographics
            first_names = ["Rajesh", "Priya", "Anil", "Sunita", "Vikram", "Anita", "Kumar", "Deepa"]
            last_names = ["Kumar", "Singh", "Patel", "Sharma", "Verma", "Khan", "Reddy", "Gupta"]
            
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            
            beneficiaries.append({
                "beneficiary_id": beneficiary_id,
                "household_id": household_id,
                "name": name,
                "age": random.randint(18, 80),
                "gender": random.choice(["M", "F"]),
                "aadhaar_hash": f"AAD{i:08d}",  # Simulated hash
                "income_band": random.choice(DataGenerator.INCOME_BANDS),
                "caste_category": random.choice(DataGenerator.CASTE_CATEGORIES),
                "family_size": random.randint(2, 10),
                "district": district,
                "state": state,
                "latitude": round(random.uniform(12.0, 35.0), 4),
                "longitude": round(random.uniform(68.0, 97.0), 4),
                "distance_to_hospital_km": round(random.uniform(1, 100), 2),
                "is_enrolled": bool(np.random.choice([True, False], p=[0.85, 0.15])), # 85% enrolled
                "enrollment_date": datetime.now() - timedelta(days=random.randint(0, 365)) if random.choice([True, False]) else None
            })
        
        df = pd.DataFrame(beneficiaries)
        
        print(f"✓ Generated {num_beneficiaries} beneficiaries")
        print(f"✓ Enrollment rate: {(df['is_enrolled'].sum() / len(df) * 100):.2f}%")
        
        return df
    
    @staticmethod
    def generate_hospital_data(num_hospitals: int = 150) -> pd.DataFrame:
        """
        Generate synthetic hospital/facility data.
        
        Args:
            num_hospitals (int): Number of hospitals to generate
        
        Returns:
            pd.DataFrame: Hospital dataset
        """
        
        print(f"🔄 Generating {num_hospitals} synthetic hospitals...")
        
        hospitals = []
        
        hospital_names = [
            "Max Healthcare", "Apollo Hospitals", "Fortis", "Manipal", "AIIMS",
            "Government Medical College", "Indore Hospital", "City Clinic",
            "Health Plus", "Care Hospital", "Life Care", "Prime Hospital"
        ]
        
        for i in range(num_hospitals):
            hospital_id = f"HOS{i:04d}"
            district = random.choice(DataGenerator.DISTRICTS)
            state = DataGenerator.STATES[district]
            
            hospitals.append({
                "hospital_id": hospital_id,
                "name": f"{random.choice(hospital_names)} - {district}",
                "state": state,
                "district": district,
                "latitude": round(random.uniform(12.0, 35.0), 4),
                "longitude": round(random.uniform(68.0, 97.0), 4),
                "hospital_type": random.choice(DataGenerator.HOSPITAL_TYPES),
                "is_empanelled": bool(np.random.choice([True, False], p=[0.95, 0.05])),
                "claim_frequency": random.randint(10, 500),
                "average_claim_amount": round(random.uniform(15000, 400000), 2),
                "rejection_rate": round(random.uniform(0, 0.15), 4) * 100  # 0-15% rejection
            })
        
        df = pd.DataFrame(hospitals)
        
        print(f"✓ Generated {num_hospitals} hospitals")
        print(f"✓ Empanelled rate: {(df['is_empanelled'].sum() / len(df) * 100):.2f}%")
        
        return df
    
    @staticmethod
    def save_datasets(
        claims_df: pd.DataFrame,
        beneficiaries_df: pd.DataFrame,
        hospitals_df: pd.DataFrame,
        output_dir: str = "app/data"
    ):
        """
        Save generated datasets to CSV files.
        
        Args:
            claims_df (pd.DataFrame): Claims dataset
            beneficiaries_df (pd.DataFrame): Beneficiaries dataset
            hospitals_df (pd.DataFrame): Hospitals dataset
            output_dir (str): Directory to save files
        """
        
        os.makedirs(output_dir, exist_ok=True)
        
        claims_path = os.path.join(output_dir, "mock_claims.csv")
        beneficiaries_path = os.path.join(output_dir, "mock_beneficiaries.csv")
        hospitals_path = os.path.join(output_dir, "mock_hospitals.csv")
        
        claims_df.to_csv(claims_path, index=False)
        beneficiaries_df.to_csv(beneficiaries_path, index=False)
        hospitals_df.to_csv(hospitals_path, index=False)
        
        print(f"\n✓ Saved: {claims_path}")
        print(f"✓ Saved: {beneficiaries_path}")
        print(f"✓ Saved: {hospitals_path}")


# Script to generate data
if __name__ == "__main__":
    print("=" * 60)
    print("PM-JAY SYNTHETIC DATA GENERATOR")
    print("=" * 60)
    
    generator = DataGenerator()
    
    # Generate datasets
    claims_df = generator.generate_claims_data(num_claims=10000)
    beneficiaries_df = generator.generate_beneficiary_data(num_beneficiaries=5000)
    hospitals_df = generator.generate_hospital_data(num_hospitals=150)
    
    # Save to CSV
    generator.save_datasets(claims_df, beneficiaries_df, hospitals_df)
    
    print("\n" + "=" * 60)
    print("✓ DATA GENERATION COMPLETE")
    print("=" * 60)
    print(f"\nClaims Dataset:")
    print(claims_df.head())
    print(f"\nBeneficiaries Dataset:")
    print(beneficiaries_df.head())
    print(f"\nHospitals Dataset:")
    print(hospitals_df.head())