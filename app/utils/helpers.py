"""
Helper functions for common operations.
"""

import hashlib
from datetime import datetime
from typing import Any, Dict


def hash_aadhaar(aadhaar: str) -> str:
    """
    Hash an Aadhaar number for privacy.
    
    Args:
        aadhaar (str): Aadhaar number to hash
    
    Returns:
        str: SHA-256 hash of the Aadhaar number
    """
    return hashlib.sha256(aadhaar.encode()).hexdigest()


def create_hash_chain(data: str, previous_hash: str = None) -> str:
    """
    Create a hash chain entry for immutable audit logs.
    
    Args:
        data (str): Data to hash
        previous_hash (str, optional): Previous hash in chain
    
    Returns:
        str: SHA-256 hash for this entry in the chain
    """
    if previous_hash:
        combined = f"{data}{previous_hash}"
    else:
        combined = data
    
    return hashlib.sha256(combined.encode()).hexdigest()


def format_currency(amount: float, currency: str = "INR") -> str:
    """
    Format amount as currency string.
    
    Args:
        amount (float): Amount to format
        currency (str): Currency code (default: INR)
    
    Returns:
        str: Formatted currency string
    """
    if currency == "INR":
        return f"₹{amount:,.2f}"
    return f"{amount:,.2f} {currency}"


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates (Haversine formula).
    
    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates
    
    Returns:
        float: Distance in kilometers
    """
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371  # Earth radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c