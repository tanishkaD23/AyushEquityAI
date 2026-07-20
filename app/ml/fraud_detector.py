"""
Fraud detection model using Isolation Forest.
Trained on synthetic claims data to detect suspicious patterns.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pickle
import os
from typing import Tuple, List, Dict
import warnings

warnings.filterwarnings('ignore')


class FraudDetector:
    """
    Isolation Forest-based fraud detection model.
    Detects anomalous claims that deviate from normal patterns.
    """
    
    def __init__(self, contamination: float = 0.10):
        """
        Initialize fraud detector.
        
        Args:
            contamination (float): Expected proportion of outliers (fraud)
        """
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.feature_names = None
        self.is_trained = False
        self.version = "1.0.0"
    
    def prepare_features(self, claims_df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare and engineer features for fraud detection.
        
        Args:
            claims_df (pd.DataFrame): Claims dataset
        
        Returns:
            pd.DataFrame: Prepared features
        """
        
        features = pd.DataFrame()
        
        # Numerical features
        features['billed_amount'] = claims_df['billed_amount']
        features['treatment_duration_days'] = claims_df['treatment_duration_days']
        features['patient_age'] = claims_df['patient_age']
        features['claim_frequency_for_hospital'] = claims_df['claim_frequency_for_hospital']
        features['claim_frequency_for_patient'] = claims_df['claim_frequency_for_patient']
        features['days_since_last_claim'] = claims_df['days_since_last_claim']
        
        # Engineered features
        features['amount_per_day'] = (
            claims_df['billed_amount'] / (claims_df['treatment_duration_days'] + 1)
        )
        
        features['hospital_frequency_normalized'] = (
            claims_df['claim_frequency_for_hospital'] / 
            (claims_df['claim_frequency_for_hospital'].max() + 1)
        )
        
        features['patient_frequency_normalized'] = (
            claims_df['claim_frequency_for_patient'] / 
            (claims_df['claim_frequency_for_patient'].max() + 1)
        )
        
        # Handle missing values
        features = features.fillna(0)
        
        self.feature_names = features.columns.tolist()
        
        return features
    
    def train(self, claims_df: pd.DataFrame) -> Dict[str, float]:
        """
        Train the Isolation Forest model on claims data.
        
        Args:
            claims_df (pd.DataFrame): Claims dataset with features
        
        Returns:
            dict: Training metrics
        """
        
        print("🔄 Preparing features for fraud detection...")
        X = self.prepare_features(claims_df)
        
        print("🔄 Training Isolation Forest model...")
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        
        # Get predictions and scores
        predictions = self.model.predict(X_scaled)
        anomaly_scores = self.model.score_samples(X_scaled)
        
        # Calculate metrics
        n_fraud = (predictions == -1).sum()
        n_legitimate = (predictions == 1).sum()
        fraud_rate = n_fraud / len(predictions) * 100
        
        self.is_trained = True
        
        metrics = {
            "total_claims": len(predictions),
            "flagged_fraud": int(n_fraud),
            "legitimate": int(n_legitimate),
            "fraud_rate": fraud_rate,
            "mean_anomaly_score": float(anomaly_scores.mean()),
            "min_anomaly_score": float(anomaly_scores.min()),
            "max_anomaly_score": float(anomaly_scores.max())
        }
        
        print(f"✓ Model trained successfully!")
        print(f"✓ Total claims: {metrics['total_claims']}")
        print(f"✓ Flagged as fraud: {metrics['flagged_fraud']} ({fraud_rate:.2f}%)")
        
        return metrics
    
    def predict(self, features_df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict fraud on new claims.
        
        Args:
            features_df (pd.DataFrame): Features for new claims
        
        Returns:
            Tuple containing:
                - predictions: -1 for fraud, 1 for legitimate
                - scores: Anomaly scores (lower = more anomalous)
        """
        
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        X_scaled = self.scaler.transform(features_df)
        predictions = self.model.predict(X_scaled)
        scores = self.model.score_samples(X_scaled)
        
        return predictions, scores
    
    def predict_proba_fraud(self, features_df: pd.DataFrame) -> np.ndarray:
        """
        Get fraud probability scores (0-100).
        
        Args:
            features_df (pd.DataFrame): Features for new claims
        
        Returns:
            np.ndarray: Fraud probability scores (0-100)
        """
        
        predictions, scores = self.predict(features_df)
        
        # Normalize scores to 0-100 probability
        # Lower scores = more anomalous = higher fraud probability
        scores_normalized = (1 - (scores - scores.min()) / (scores.max() - scores.min() + 1e-10)) * 100
        
        return scores_normalized
    
    def save_model(self, filepath: str = "app/ml/models/fraud_detector.pkl"):
        """
        Save trained model to disk.
        
        Args:
            filepath (str): Path to save model
        """
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        model_data = {
            "model": self.model,
            "scaler": self.scaler,
            "feature_names": self.feature_names,
            "version": self.version,
            "is_trained": self.is_trained
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"✓ Model saved: {filepath}")
    
    @staticmethod
    def load_model(filepath: str = "app/ml/models/fraud_detector.pkl") -> 'FraudDetector':
        """
        Load trained model from disk.
        
        Args:
            filepath (str): Path to load model
        
        Returns:
            FraudDetector: Loaded model instance
        """
        
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        detector = FraudDetector()
        detector.model = model_data["model"]
        detector.scaler = model_data["scaler"]
        detector.feature_names = model_data["feature_names"]
        detector.version = model_data["version"]
        detector.is_trained = model_data["is_trained"]
        
        print(f"✓ Model loaded: {filepath}")
        
        return detector
    
    def get_model_info(self) -> Dict:
        """Get information about the fraud detector model."""
        return {
            "model_name": "Isolation Forest Fraud Detector",
            "version": self.version,
            "is_trained": self.is_trained,
            "features": self.feature_names,
            "algorithm": "Isolation Forest",
            "contamination": "0.10 (10% expected fraud rate)",
            "n_estimators": 100
        }


# Training script
if __name__ == "__main__":
    print("=" * 60)
    print("FRAUD DETECTION MODEL TRAINING")
    print("=" * 60)
    
    # Load claims data
    claims_df = pd.read_csv("app/data/mock_claims.csv")
    
    print(f"\n📊 Loaded {len(claims_df)} claims for training\n")
    
    # Train model
    detector = FraudDetector(contamination=0.10)
    metrics = detector.train(claims_df)
    
    print(f"\n📈 Training Metrics:")
    for key, value in metrics.items():
        print(f"   {key}: {value}")
def detect_duplicate_claims(
    self,
    claims_df: pd.DataFrame,
    similarity_threshold: float = 0.95
) -> pd.DataFrame:
    """
    Detect duplicate claims using fuzzy matching on key attributes.
    
    Args:
        claims_df (pd.DataFrame): Claims to check
        similarity_threshold (float): Threshold for duplicate detection
    
    Returns:
        pd.DataFrame: Potential duplicates
    """
    
    from difflib import SequenceMatcher
    
    duplicates = []
    
    # Group by beneficiary to find duplicate claims
    for beneficiary_id, group in claims_df.groupby('beneficiary_id'):
        if len(group) < 2:
            continue
        
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                claim1 = group.iloc[i]
                claim2 = group.iloc[j]
                
                # Check if same treatment within 7 days
                date1 = pd.to_datetime(claim1['claim_date'])
                date2 = pd.to_datetime(claim2['claim_date'])
                days_diff = abs((date2 - date1).days)
                
                if days_diff <= 7 and claim1['treatment_code'] == claim2['treatment_code']:
                    # Check amount similarity
                    amount_similarity = min(claim1['billed_amount'], claim2['billed_amount']) / \
                                       max(claim1['billed_amount'], claim2['billed_amount'])
                    
                    if amount_similarity > 0.9:
                        duplicates.append({
                            "claim1_id": claim1['claim_id'],
                            "claim2_id": claim2['claim_id'],
                            "days_apart": days_diff,
                            "amount_similarity": amount_similarity,
                            "duplicate_confidence": 0.95,
                            "fraud_indicator": "likely_duplicate"
                        })
    
    return pd.DataFrame(duplicates) if duplicates else pd.DataFrame()

def detect_impossible_travel(
    self,
    claims_df: pd.DataFrame,
    hospitals_df: pd.DataFrame,
    beneficiaries_df: pd.DataFrame,
    max_travel_speed_kmh: float = 100  # km/hour
) -> pd.DataFrame:
    """
    Detect impossible travel patterns (same patient in distant locations same day).
    
    Args:
        claims_df (pd.DataFrame): Claims
        hospitals_df (pd.DataFrame): Hospital locations
        beneficiaries_df (pd.DataFrame): Beneficiary locations
        max_travel_speed_kmh (float): Maximum realistic travel speed
    
    Returns:
        pd.DataFrame: Impossible travel instances
    """
    
    from math import radians, sin, cos, sqrt, atan2
    
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c
    
    impossible_travels = []
    
    # Check each beneficiary
    for beneficiary_id, group in claims_df.groupby('beneficiary_id'):
        group = group.sort_values('claim_date')
        
        if len(group) < 2:
            continue
        
        for i in range(len(group) - 1):
            claim1 = group.iloc[i]
            claim2 = group.iloc[i + 1]
            
            # Same day claims
            date1 = pd.to_datetime(claim1['claim_date']).date()
            date2 = pd.to_datetime(claim2['claim_date']).date()
            
            if date1 == date2:
                # Get hospital locations
                hosp1 = hospitals_df[hospitals_df['hospital_id'] == claim1['hospital_id']]
                hosp2 = hospitals_df[hospitals_df['hospital_id'] == claim2['hospital_id']]
                
                if len(hosp1) > 0 and len(hosp2) > 0:
                    distance = haversine(
                        hosp1.iloc[0]['latitude'],
                        hosp1.iloc[0]['longitude'],
                        hosp2.iloc[0]['latitude'],
                        hosp2.iloc[0]['longitude']
                    )
                    
                    # Time gap (assume 30 minutes between claims)
                    time_gap_hours = 0.5
                    max_possible_distance = max_travel_speed_kmh * time_gap_hours
                    
                    if distance > max_possible_distance:
                        impossible_travels.append({
                            "beneficiary_id": beneficiary_id,
                            "claim1_id": claim1['claim_id'],
                            "claim2_id": claim2['claim_id'],
                            "distance_km": distance,
                            "max_possible_km": max_possible_distance,
                            "fraud_confidence": 0.98,
                            "fraud_indicator": "impossible_travel"
                        })
    
    return pd.DataFrame(impossible_travels) if impossible_travels else pd.DataFrame()        
    
    # Save model
    detector.save_model()
    
    print("\n" + "=" * 60)
    print("✓ TRAINING COMPLETE")
    print("=" * 60)