"""
Complete Day 4-6 setup script.
Generates all required files in correct sequence.
"""

import os
import sys
import subprocess

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 70)
print("AYUSHEQUITYAI - DAY 4-6 COMPLETE SETUP")
print("=" * 70)

# Check if mock data exists
required_files = [
    "app/data/mock_claims.csv",
    "app/data/mock_beneficiaries.csv",
    "app/data/mock_hospitals.csv",
    "app/data/hospital_features.csv",
    "app/data/inclusion_pipeline_results.csv"
]

print("\n✓ Checking prerequisite files...")
missing_files = [f for f in required_files if not os.path.exists(f)]

if missing_files:
    print(f"❌ Missing files:")
    for f in missing_files:
        print(f"   - {f}")
    print("\n⚠️  Please run Day 1-3 setup first:")
    print("   python app/data/data_generator.py")
    print("   python app/ml/fraud_detector.py")
    print("   python app/ml/hospital_features.py")
    print("   python app/ml/inclusion_matcher.py")
    print("   python app/ml/equity_scorer.py")
    print("   python app/ml/inclusion_pipeline.py")
    sys.exit(1)

print("✓ All prerequisite files found!")

# Now run Day 4-6 modules in sequence
print("\n" + "=" * 70)
print("RUNNING DAY 4 MODULES")
print("=" * 70)

# Step 1: Hospital Risk Scorer
print("\n[1/3] Hospital Risk Scorer...")
try:
    import pandas as pd
    from app.ml.hospital_risk_scorer import HospitalRiskScorer
    
    claims_df = pd.read_csv("app/data/mock_claims.csv")
    hospital_features_df = pd.read_csv("app/data/hospital_features.csv")
    
    risk_scores = HospitalRiskScorer.score_hospitals(claims_df, hospital_features_df)
    risk_scores.to_csv("app/data/hospital_risk_scores.csv", index=False)
    
    print("✓ Created: app/data/hospital_risk_scores.csv")
except Exception as e:
    print(f"❌ Error in Hospital Risk Scorer: {str(e)}")
    sys.exit(1)

print("\n[2/3] Inclusion Pipeline...")
try:
    from app.ml.inclusion_pipeline import InclusionAIPipeline
    
    beneficiaries_df = pd.read_csv("app/data/mock_beneficiaries.csv")
    
    pipeline = InclusionAIPipeline()
    results = pipeline.process_all_districts(beneficiaries_df)
    results.to_csv("app/data/inclusion_pipeline_results.csv", index=False)
    
    print("✓ Created: app/data/inclusion_pipeline_results.csv")
except Exception as e:
    print(f"❌ Error in Inclusion Pipeline: {str(e)}")
    sys.exit(1)

print("\n" + "=" * 70)
print("RUNNING DAY 5 MODULES")
print("=" * 70)

print("\n[3/3] District Analytics...")
try:
    from app.ml.district_analytics import DistrictAnalytics
    
    beneficiaries_df = pd.read_csv("app/data/mock_beneficiaries.csv")
    claims_df = pd.read_csv("app/data/mock_claims.csv")
    inclusion_df = pd.read_csv("app/data/inclusion_pipeline_results.csv")
    hospital_risk_df = pd.read_csv("app/data/hospital_risk_scores.csv")
    equity_df = pd.read_csv("app/data/district_equity_scores.csv")
    
    analytics = DistrictAnalytics()
    report = analytics.create_district_report(
        beneficiaries_df, 
        inclusion_df, 
        hospital_risk_df, 
        equity_df
    )
    
    report.to_csv("app/data/district_analytics_report.csv", index=False)
    
    print("✓ Created: app/data/district_analytics_report.csv")
except Exception as e:
    print(f"❌ Error in District Analytics: {str(e)}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ SETUP COMPLETE - ALL FILES GENERATED")
print("=" * 70)

print("\n📊 Generated Files:")
output_files = [
    "app/data/hospital_risk_scores.csv",
    "app/data/inclusion_pipeline_results.csv",
    "app/data/district_analytics_report.csv"
]

for f in output_files:
    if os.path.exists(f):
        size = os.path.getsize(f)
        print(f"✓ {f} ({size:,} bytes)")

print("\n🚀 Next Steps:")
print("1. Start FastAPI backend:")
print("   python main.py")
print("\n2. In another terminal, start Streamlit:")
print("   streamlit run app/frontend/app.py")
print("\n3. Open browser:")
print("   http://localhost:8501")

print("\n" + "=" * 70)
print("Happy Demoing! 🎉")
print("=" * 70)