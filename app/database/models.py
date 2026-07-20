"""
SQLAlchemy ORM models for AyushEquityAI database.
Defines all database tables and relationships.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base import Base


class Beneficiary(Base):
    """
    Beneficiary/Household model.
    Stores information about eligible households under PM-JAY.
    """
    __tablename__ = "beneficiaries"
    
    id = Column(Integer, primary_key=True, index=True)
    beneficiary_id = Column(String(50), unique=True, index=True)
    household_id = Column(String(50), index=True)
    name = Column(String(255))
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    aadhaar_hash = Column(String(100), nullable=True)  # Hashed for privacy
    
    # Socio-economic information
    income_band = Column(String(50), nullable=True)  # BPL, APL, EWS, etc.
    caste_category = Column(String(50), nullable=True)
    family_size = Column(Integer, nullable=True)
    
    # Location information
    district = Column(String(100), index=True)
    state = Column(String(100))
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    distance_to_hospital = Column(Float, nullable=True)  # in km
    
    # Enrollment status
    is_enrolled = Column(Boolean, default=False)
    enrollment_date = Column(DateTime, nullable=True)
    
    # Inclusion AI scores
    inclusion_score = Column(Float, nullable=True)  # 0-100
    equity_score = Column(Float, nullable=True)  # 0-100
    priority_rank = Column(Integer, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    claims = relationship("Claim", back_populates="beneficiary")
    eligibility_checks = relationship("EligibilityCheck", back_populates="beneficiary")


class Household(Base):
    """
    Extended household information for demographics and eligibility.
    """
    __tablename__ = "households"
    
    id = Column(Integer, primary_key=True, index=True)
    household_id = Column(String(50), unique=True, index=True)
    head_name = Column(String(255))
    head_aadhaar_hash = Column(String(100), nullable=True)
    
    income_band = Column(String(50))
    family_size = Column(Integer)
    caste_category = Column(String(50), nullable=True)
    
    district = Column(String(100), index=True)
    state = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Eligibility criteria
    has_digital_records = Column(Boolean, default=False)
    is_pm_jay_eligible = Column(Boolean, default=False)
    eligibility_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Hospital(Base):
    """
    Hospital/Healthcare facility information.
    """
    __tablename__ = "hospitals"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(String(50), unique=True, index=True)
    name = Column(String(255))
    state = Column(String(100))
    district = Column(String(100), index=True)
    
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Hospital characteristics
    empanelled_date = Column(DateTime, nullable=True)
    is_empanelled = Column(Boolean, default=True)
    hospital_type = Column(String(50))  # Government, Private, NGO
    
    # Risk scoring
    fraud_risk_score = Column(Float, nullable=True)  # 0-100
    claim_frequency = Column(Integer, default=0)
    average_claim_amount = Column(Float, nullable=True)
    rejection_rate = Column(Float, nullable=True)  # 0-100
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    claims = relationship("Claim", back_populates="hospital")


class Claim(Base):
    """
    Healthcare claim submitted by hospital.
    """
    __tablename__ = "claims"
    
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(String(50), unique=True, index=True)
    beneficiary_id = Column(Integer, ForeignKey("beneficiaries.id"))
    hospital_id = Column(Integer, ForeignKey("hospitals.id"))
    
    treatment_code = Column(String(50), index=True)
    treatment_description = Column(Text)
    billed_amount = Column(Float)
    approved_amount = Column(Float, nullable=True)
    
    claim_date = Column(DateTime)
    approval_date = Column(DateTime, nullable=True)
    
    # Fraud detection flags
    fraud_score = Column(Float, nullable=True)  # 0-100
    is_flagged = Column(Boolean, default=False)
    flag_reason = Column(Text, nullable=True)
    
    # Status
    status = Column(String(50), default="submitted")  # submitted, approved, rejected, flagged
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    beneficiary = relationship("Beneficiary", back_populates="claims")
    hospital = relationship("Hospital", back_populates="claims")
    audit_logs = relationship("AuditLog", back_populates="claim")


class EligibilityCheck(Base):
    """
    Records of eligibility verification checks.
    """
    __tablename__ = "eligibility_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    beneficiary_id = Column(Integer, ForeignKey("beneficiaries.id"))
    
    check_date = Column(DateTime, default=datetime.utcnow)
    is_eligible = Column(Boolean)
    eligibility_reason = Column(Text)
    
    # Source of verification
    verification_method = Column(String(50))  # rule_engine, ml_model, manual, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    beneficiary = relationship("Beneficiary", back_populates="eligibility_checks")


class AuditLog(Base):
    """
    Immutable audit log for all claim actions.
    Supports tamper-evident verification via hash chain.
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), index=True)
    
    action = Column(String(50))  # approve, reject, flag, review, etc.
    officer_id = Column(String(50), nullable=True)
    officer_name = Column(String(255), nullable=True)
    
    reason = Column(Text, nullable=True)
    
    # Hash chain for tamper-evidence
    action_hash = Column(String(256))  # SHA-256 of this action
    previous_hash = Column(String(256), nullable=True)  # SHA-256 of previous action
    is_chain_valid = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    claim = relationship("Claim", back_populates="audit_logs")