"""Pydantic schemas for the entire application."""

from __future__ import annotations
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


# ────────────────────── Enums ──────────────────────

class DocumentType(str, Enum):
    AADHAAR = "aadhaar"
    PAN = "pan"
    INCOME_CERT = "income_certificate"
    BANK_STMT = "bank_statement"
    BIRTH_CERT = "birth_certificate"
    LAND_RECORD = "land_record"
    OTHER = "other"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ApplicationStatus(str, Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    FLAGGED = "flagged"
    REJECTED = "rejected"


class DecisionAction(str, Enum):
    APPROVE = "approve"
    FLAG = "flag"
    REJECT = "reject"


# ────────────────────── Extracted Fields ──────────────────────

class ExtractedFields(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    aadhaar_number: Optional[str] = None
    pan_number: Optional[str] = None
    income_monthly: Optional[float] = None
    bank_account: Optional[str] = None
    phone: Optional[str] = None
    document_type: DocumentType = DocumentType.OTHER
    confidence: float = 0.0
    raw_text: str = ""
    language_detected: str = "en"


# ────────────────────── Discrepancy ──────────────────────

class Discrepancy(BaseModel):
    field: str
    declared_value: str
    extracted_value: str
    source_document: str
    severity: Severity
    match_score: float = Field(ge=0.0, le=1.0)
    details: str


# ────────────────────── Risk Score ──────────────────────

class RiskFactor(BaseModel):
    rule_id: str
    rule_name: str
    points: int
    description: str
    confidence: str = "high"  # high / medium / low


class RiskScore(BaseModel):
    score: int = Field(ge=0, le=100)
    risk_level: RiskLevel
    factors: list[RiskFactor] = []
    recommended_action: str = "manual_review"
    comparable_cases: list[str] = []


# ────────────────────── Application ──────────────────────

class DeclaredValues(BaseModel):
    full_name: str
    date_of_birth: str
    gender: str = "male"
    address: str = ""
    aadhaar_number: str = ""
    pan_number: str = ""
    income_monthly: float = 0.0
    bank_account: str = ""
    phone: str = ""
    scheme: str = "PM-KISAN"
    state: str = ""
    district: str = ""


class ApplicationCreate(BaseModel):
    declared: DeclaredValues
    documents: list[dict] = []  # pre-attached doc references


class ApplicationResponse(BaseModel):
    id: str
    declared: DeclaredValues
    status: ApplicationStatus = ApplicationStatus.PENDING
    risk_score: Optional[RiskScore] = None
    discrepancies: list[Discrepancy] = []
    explanation: Optional[str] = None
    explanation_audio_url: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""


class ApplicationListItem(BaseModel):
    id: str
    applicant_name: str
    scheme: str
    status: ApplicationStatus
    risk_score: Optional[int] = None
    risk_level: Optional[RiskLevel] = None
    created_at: str


# ────────────────────── Document Upload ──────────────────────

class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    document_type: DocumentType
    extracted_fields: Optional[ExtractedFields] = None
    raw_ocr_text: str = ""
    status: str = "processed"


# ────────────────────── Decision ──────────────────────

class OfficerDecision(BaseModel):
    action: DecisionAction
    reason: str = ""
    officer_id: str = "officer-1"


# ────────────────────── Voice ──────────────────────

class TranscriptionResponse(BaseModel):
    transcript: str
    language_detected: str = "hi-IN"
    confidence: float = 0.0


class VoiceQueryResponse(BaseModel):
    transcript: str
    language_detected: str
    response_text: str
    response_language: str
    audio_base64: Optional[str] = None


# ────────────────────── Explanation ──────────────────────

class ExplainRequest(BaseModel):
    language: str = "en"


class ExplainResponse(BaseModel):
    explanation: str
    language: str
    audio_base64: Optional[str] = None


# ────────────────────── Stats ──────────────────────

class DashboardStats(BaseModel):
    total_applications: int = 0
    pending: int = 0
    approved: int = 0
    flagged: int = 0
    rejected: int = 0
    avg_risk_score: float = 0.0
    high_risk_count: int = 0
