"""Pydantic schemas for the entire application."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


# ────────────────────── Enums ──────────────────────


class DocumentType(str, Enum):
    AADHAAR = "aadhaar"
    PAN = "pan"
    INCOME_CERT = "income_certificate"
    BANK_STMT = "bank_statement"
    BIRTH_CERT = "birth_certificate"
    LAND_RECORD = "land_record"
    VOTER_ID = "voter_id"
    RATION_CARD = "ration_card"
    OTHER = "other"


class RiskBand(str, Enum):
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
    ESCALATED = "escalated"


class DecisionAction(str, Enum):
    APPROVE = "approve"
    FLAG = "flag"
    REJECT = "reject"
    ESCALATE = "escalate"


class SourceAccessMode(str, Enum):
    LIVE = "live"
    BATCH = "batch"
    CACHED = "cached"
    SYNTHETIC = "synthetic"


# ────────────────────── Core domain models ──────────────────────


class ExtractedFields(BaseModel):
    full_name: str | None = None
    dob: str | None = None
    gender: str | None = None
    address: str | None = None
    aadhaar_masked: str | None = None
    pan_masked: str | None = None
    income_monthly: float | None = None
    bank_account_masked: str | None = None
    phone_masked: str | None = None
    document_type: DocumentType = DocumentType.OTHER
    confidence: float = 0.0
    raw_text: str = ""
    language_detected: str = "en-IN"


class DeclaredValues(BaseModel):
    full_name: str
    dob: str = ""
    gender: str = "male"
    address: str = ""
    aadhaar_masked: str = ""
    pan_masked: str = ""
    income_monthly: float = 0.0
    bank_account_masked: str = ""
    phone_masked: str = ""
    scheme: str = "PM-KISAN"
    state: str = ""
    district: str = ""


class Discrepancy(BaseModel):
    field: str
    declared_value: str
    extracted_value: str
    source_document: str
    severity: Severity
    match_score: float = Field(ge=0.0, le=1.0)
    details: str = ""
    evidence_uri: str | None = None


class RiskFactor(BaseModel):
    factor_id: str
    factor_name: str
    points: int = 0
    max_points: int = 0
    description: str = ""
    confidence: float = 1.0
    source_ref: str = ""


class AnomalyFinding(BaseModel):
    anomaly_type: str
    description: str = ""
    severity: Severity = Severity.MEDIUM
    contributing_score: int = 0
    evidence: str = ""


class NetworkFlag(BaseModel):
    flag_type: str
    description: str = ""
    linked_entity_ids: list[str] = []
    confidence: float = 0.0


class SourceReliability(BaseModel):
    source_name: str
    source_trust_score: float = Field(ge=0.0, le=1.0, default=1.0)
    last_updated_at: str | None = None
    access_mode: SourceAccessMode = SourceAccessMode.SYNTHETIC
    evidence_uri: str | None = None


class CanonicalRiskProfile(BaseModel):
    case_id: str
    beneficiary_entity_id: str = ""
    risk_score: int = Field(ge=0, le=100, default=0)
    risk_band: RiskBand = RiskBand.LOW
    factors: list[RiskFactor] = []
    anomalies: list[AnomalyFinding] = []
    network_flags: list[NetworkFlag] = []
    recommended_action: str = "manual_review"
    confidence: float = 0.0
    explanation_text: str = ""
    explanation_audio_url: str | None = None


class ConnectorResult(BaseModel):
    source_name: str
    data: dict = {}
    reliability: SourceReliability | None = None


# ────────────────────── API request / response models ──────────────────────


class ApplicationCreate(BaseModel):
    declared: DeclaredValues
    documents: list[dict] = []


class ApplicationResponse(BaseModel):
    id: str
    declared: DeclaredValues
    status: ApplicationStatus = ApplicationStatus.PENDING
    risk_score: int | None = None
    risk_band: RiskBand | None = None
    risk_profile: CanonicalRiskProfile | None = None
    discrepancies: list[Discrepancy] = []
    explanation: str | None = None
    explanation_audio_url: str | None = None
    created_at: str = ""
    updated_at: str = ""


class ApplicationListItem(BaseModel):
    id: str
    applicant_name: str
    scheme: str
    status: ApplicationStatus
    risk_score: int | None = None
    risk_band: RiskBand | None = None
    created_at: str


class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    document_type: DocumentType
    extracted_fields: ExtractedFields | None = None
    raw_ocr_text: str = ""
    status: str = "processed"


class OfficerDecision(BaseModel):
    action: DecisionAction
    reason: str = ""
    officer_id: str = "officer-1"


class TranscriptionResponse(BaseModel):
    transcript: str
    language_detected: str = "hi-IN"
    confidence: float = 0.0


class VoiceQueryResponse(BaseModel):
    transcript: str
    language_detected: str
    response_text: str
    response_language: str
    audio_base64: str | None = None


class ExplainRequest(BaseModel):
    language: str = "en-IN"


class ExplainResponse(BaseModel):
    explanation: str
    language: str
    audio_base64: str | None = None


class DashboardStats(BaseModel):
    total_applications: int = 0
    pending: int = 0
    under_review: int = 0
    approved: int = 0
    flagged: int = 0
    rejected: int = 0
    escalated: int = 0
    avg_risk_score: float = 0.0
    high_risk_count: int = 0
