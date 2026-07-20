"""
Fuzzy matching engine for inclusion AI.
Matches households against enrolled beneficiaries.
"""

import pandas as pd
from difflib import SequenceMatcher
from typing import Tuple, List, Dict
import numpy as np


class InclusionMatcher:
    """
    Fuzzy name + Aadhaar matching for identifying unenrolled eligible households.
    """
    
    def __init__(self, match_threshold: float = 0.85):
        """
        Initialize matcher.
        
        Args:
            match_threshold (float): Similarity threshold for matching (0-1)
        """
        self.match_threshold = match_threshold
        self.enrolled_beneficiaries = None
        self.version = "1.0.0"
    
    def load_enrolled_beneficiaries(self, beneficiaries_df: pd.DataFrame):
        """
        Load enrolled beneficiaries for matching.
        
        Args:
            beneficiaries_df (pd.DataFrame): Beneficiary dataset
        """
        # Filter to only enrolled
        self.enrolled_beneficiaries = beneficiaries_df[
            beneficiaries_df['is_enrolled'] == True
        ].copy()
        
        print(f"✓ Loaded {len(self.enrolled_beneficiaries)} enrolled beneficiaries")
    
    @staticmethod
    def _name_similarity(name1: str, name2: str) -> float:
        """
        Calculate name similarity using SequenceMatcher.
        
        Args:
            name1, name2 (str): Names to compare
        
        Returns:
            float: Similarity score (0-1)
        """
        name1 = name1.lower().strip()
        name2 = name2.lower().strip()
        
        return SequenceMatcher(None, name1, name2).ratio()
    
    @staticmethod
    def _aadhaar_similarity(aadhaar1: str, aadhaar2: str, tolerance: int = 2) -> float:
        """
        Compare Aadhaar hashes with tolerance for OCR errors.
        
        Args:
            aadhaar1, aadhaar2 (str): Aadhaar hashes
            tolerance (int): Number of character differences allowed
        
        Returns:
            float: Similarity score (0-1)
        """
        if not aadhaar1 or not aadhaar2:
            return 0.0
        
        # Count matching characters
        matches = sum(c1 == c2 for c1, c2 in zip(aadhaar1, aadhaar2))
        max_len = max(len(aadhaar1), len(aadhaar2))
        
        similarity = matches / max_len
        
        # Add bonus if difference is within tolerance
        if abs(len(aadhaar1) - len(aadhaar2)) <= tolerance:
            similarity += 0.1
        
        return min(similarity, 1.0)
    
    def match_household(
        self,
        household_name: str,
        household_aadhaar: str = None,
        district: str = None
    ) -> Tuple[bool, float, Dict]:
        """
        Match a household against enrolled beneficiaries.
        
        Args:
            household_name (str): Head of household name
            household_aadhaar (str, optional): Aadhaar hash
            district (str, optional): District for geographic filtering
        
        Returns:
            Tuple containing:
                - is_match (bool): Whether a match was found
                - match_score (float): Match confidence (0-100)
                - match_info (dict): Information about the match
        """
        
        if self.enrolled_beneficiaries is None:
            raise ValueError("Must load enrolled beneficiaries first")
        
        # Filter by district if provided
        search_pool = self.enrolled_beneficiaries.copy()
        if district:
            search_pool = search_pool[search_pool['district'] == district]
        
        if len(search_pool) == 0:
            return False, 0.0, {"reason": "No beneficiaries in district"}
        
        best_score = 0.0
        best_match = None
        
        # Find best match
        for _, beneficiary in search_pool.iterrows():
            # Name similarity (60% weight)
            name_sim = self._name_similarity(household_name, beneficiary['name'])
            name_score = name_sim * 0.6
            
            # Aadhaar similarity (40% weight)
            aadhaar_score = 0.0
            if household_aadhaar and beneficiary['aadhaar_hash']:
                aadhaar_sim = self._aadhaar_similarity(
                    household_aadhaar,
                    beneficiary['aadhaar_hash']
                )
                aadhaar_score = aadhaar_sim * 0.4
            elif household_aadhaar and not beneficiary['aadhaar_hash']:
                aadhaar_score = 0.2  # Partial credit
            
            total_score = (name_score + aadhaar_score) * 100
            
            if total_score > best_score:
                best_score = total_score
                best_match = {
                    "beneficiary_id": beneficiary['beneficiary_id'],
                    "matched_name": beneficiary['name'],
                    "name_similarity": name_sim,
                    "aadhaar_similarity": aadhaar_score / 0.4 if aadhaar_score > 0 else 0
                }
        
        # Determine if it's a match
        is_match = best_score >= (self.match_threshold * 100)
        
        if is_match:
            best_match["match_type"] = "found_enrolled"
        else:
            best_match = {"match_type": "missing_unenrolled"}
        
        return is_match, best_score, best_match
    
    def find_missing_beneficiaries(
        self,
        eligible_households_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Find households that are eligible but unenrolled.
        
        Args:
            eligible_households_df (pd.DataFrame): All eligible households
        
        Returns:
            pd.DataFrame: Missing beneficiaries with priority scores
        """
        
        print(f"🔄 Matching {len(eligible_households_df)} eligible households...")
        
        results = []
        
        for idx, row in eligible_households_df.iterrows():
            is_match, score, match_info = self.match_household(
                household_name=row['name'],
                household_aadhaar=row['aadhaar_hash'],
                district=row['district']
            )
            
            result = {
                "household_id": row['household_id'],
                "name": row['name'],
                "district": row['district'],
                "is_enrolled": row['is_enrolled'],
                "match_score": score,
                "is_missing": not is_match and row['is_enrolled'] == False,
                **match_info
            }
            results.append(result)
        
        missing_df = pd.DataFrame(results)
        missing_df = missing_df[missing_df['is_missing'] == True].copy()
        
        # Calculate priority rank
        missing_df['priority_rank'] = missing_df['match_score'].rank(
            method='dense', ascending=False
        )
        
        print(f"✓ Found {len(missing_df)} missing beneficiaries")
        
        return missing_df


# Script to test inclusion matching
if __name__ == "__main__":
    print("=" * 60)
    print("INCLUSION MATCHER TEST")
    print("=" * 60)
    
    # Load data
    beneficiaries_df = pd.read_csv("app/data/mock_beneficiaries.csv")
    
    # Initialize matcher
    matcher = InclusionMatcher(match_threshold=0.85)
    matcher.load_enrolled_beneficiaries(beneficiaries_df)
    
    # Test matching
    print("\n📝 Testing individual matches...")
    test_result = matcher.match_household(
        household_name="Rajesh Kumar",
        district="Indore"
    )
    print(f"Match found: {test_result[0]}, Score: {test_result[1]:.2f}")
    
    # Find all missing
    print(f"\n🔄 Finding missing beneficiaries...")
    missing = matcher.find_missing_beneficiaries(beneficiaries_df)
    missing.to_csv("app/data/missing_beneficiaries.csv", index=False)
    
    print(f"\n✓ Saved: app/data/missing_beneficiaries.csv")
    print(f"\nTop 10 missing beneficiaries by priority:")
    print(missing.nsmallest(10, 'priority_rank')[['name', 'district', 'match_score', 'priority_rank']])