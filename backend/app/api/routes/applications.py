"""Application & verification routes — the core API surface."""

from __future__ import annotations
import json, uuid, logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    ApplicationCreate, ApplicationResponse, ApplicationListItem,
    DeclaredValues, Discrepancy, ExtractedFields, RiskScore,
    OfficerDecision, ExplainRequest, ExplainResponse,
    DashboardStats, ApplicationStatus, RiskLevel, Severity,
)
from app.core.cross_verifier import cross_verify
from app.core.risk_scorer import calculate_risk
from app.core.explainer import explain_risk
from app.core import sarvam_client
from app.data.seed_data import SEED_APPLICATIONS

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["applications"])

# ────────────────────── In-memory store (hackathon speed) ──────────────────────
# We skip SQLAlchemy for the MVP and use dicts — instant, no migrations.
_APPS: dict[str, dict] = {}
_seeded = False


def _ensure_seeded():
    """Seed the in-memory store with demo data on first access."""
    global _seeded
    if _seeded:
        return
    _seeded = True
    for seed in SEED_APPLICATIONS:
        app_id = seed["id"]
        declared = DeclaredValues(**seed["declared"])

        # Build extracted docs
        extracted_docs = []
        for doc in seed.get("documents", []):
            ef = ExtractedFields(**{
                "full_name": doc["extracted"].get("full_name"),
                "date_of_birth": doc["extracted"].get("date_of_birth"),
                "gender": doc["extracted"].get("gender"),
                "address": doc["extracted"].get("address"),
                "aadhaar_number": doc["extracted"].get("aadhaar_number"),
                "pan_number": doc["extracted"].get("pan_number"),
                "income_monthly": doc["extracted"].get("income_monthly"),
                "bank_account": doc["extracted"].get("bank_account"),
                "phone": doc["extracted"].get("phone"),
                "document_type": doc.get("type", "other"),
                "confidence": 0.9,
                "raw_text": "",
                "language_detected": "en",
            })
            extracted_docs.append((doc["source"], ef))

        # Run cross-verification
        discrepancies = cross_verify(declared, extracted_docs)

        # Calculate risk
        risk = calculate_risk(discrepancies, num_documents=len(extracted_docs))

        # Determine status based on risk
        if risk.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            status = ApplicationStatus.FLAGGED
        elif risk.risk_level == RiskLevel.MEDIUM:
            status = ApplicationStatus.UNDER_REVIEW
        else:
            status = ApplicationStatus.PENDING

        _APPS[app_id] = {
            "id": app_id,
            "declared": declared.model_dump(),
            "status": status.value,
            "risk_score": risk.model_dump(),
            "discrepancies": [d.model_dump() for d in discrepancies],
            "explanation": None,
            "documents": seed.get("documents", []),
            "created_at": "2025-04-15T10:00:00Z",
            "updated_at": "2025-04-15T10:00:00Z",
        }


# ────────────────────── Endpoints ──────────────────────

@router.get("/stats", response_model=DashboardStats)
async def get_stats():
    """Dashboard summary statistics."""
    _ensure_seeded()
    apps = list(_APPS.values())
    total = len(apps)
    risk_scores = [a["risk_score"]["score"] for a in apps if a.get("risk_score")]

    return DashboardStats(
        total_applications=total,
        pending=sum(1 for a in apps if a["status"] == "pending"),
        approved=sum(1 for a in apps if a["status"] == "approved"),
        flagged=sum(1 for a in apps if a["status"] == "flagged"),
        rejected=sum(1 for a in apps if a["status"] == "rejected"),
        avg_risk_score=sum(risk_scores) / max(len(risk_scores), 1),
        high_risk_count=sum(1 for a in apps if a.get("risk_score", {}).get("risk_level") in ("high", "critical")),
    )


@router.get("/applications", response_model=list[ApplicationListItem])
async def list_applications(
    status: str | None = None,
    risk_level: str | None = None,
    scheme: str | None = None,
    sort_by: str = "risk_score",
    sort_order: str = "desc",
):
    """List all applications with optional filters."""
    _ensure_seeded()
    apps = list(_APPS.values())

    # Filters
    if status:
        apps = [a for a in apps if a["status"] == status]
    if risk_level:
        apps = [a for a in apps if a.get("risk_score", {}).get("risk_level") == risk_level]
    if scheme:
        apps = [a for a in apps if a["declared"].get("scheme", "").lower() == scheme.lower()]

    # Sort
    def _sort_key(a):
        if sort_by == "risk_score":
            return a.get("risk_score", {}).get("score", 0)
        elif sort_by == "name":
            return a["declared"].get("full_name", "")
        elif sort_by == "created_at":
            return a.get("created_at", "")
        return 0

    apps.sort(key=_sort_key, reverse=(sort_order == "desc"))

    return [
        ApplicationListItem(
            id=a["id"],
            applicant_name=a["declared"].get("full_name", "Unknown"),
            scheme=a["declared"].get("scheme", "Unknown"),
            status=a["status"],
            risk_score=a.get("risk_score", {}).get("score"),
            risk_level=a.get("risk_score", {}).get("risk_level"),
            created_at=a.get("created_at", ""),
        )
        for a in apps
    ]


@router.get("/applications/{app_id}", response_model=ApplicationResponse)
async def get_application(app_id: str):
    """Get full application detail with risk score and discrepancies."""
    _ensure_seeded()
    app = _APPS.get(app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    return ApplicationResponse(
        id=app["id"],
        declared=DeclaredValues(**app["declared"]),
        status=app["status"],
        risk_score=RiskScore(**app["risk_score"]) if app.get("risk_score") else None,
        discrepancies=[Discrepancy(**d) for d in app.get("discrepancies", [])],
        explanation=app.get("explanation"),
        created_at=app.get("created_at", ""),
        updated_at=app.get("updated_at", ""),
    )


@router.post("/applications", response_model=ApplicationResponse)
async def create_application(body: ApplicationCreate):
    """Create a new application."""
    _ensure_seeded()
    app_id = f"APP-{str(uuid.uuid4())[:4].upper()}"
    _APPS[app_id] = {
        "id": app_id,
        "declared": body.declared.model_dump(),
        "status": ApplicationStatus.PENDING.value,
        "risk_score": None,
        "discrepancies": [],
        "explanation": None,
        "documents": body.documents,
        "created_at": "2025-04-15T12:00:00Z",
        "updated_at": "2025-04-15T12:00:00Z",
    }
    return ApplicationResponse(
        id=app_id,
        declared=body.declared,
        status=ApplicationStatus.PENDING,
    )


@router.post("/applications/{app_id}/explain", response_model=ExplainResponse)
async def explain_application(app_id: str, body: ExplainRequest = ExplainRequest()):
    """Generate a plain-language explanation of the risk assessment."""
    _ensure_seeded()
    app = _APPS.get(app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    discrepancies = [Discrepancy(**d) for d in app.get("discrepancies", [])]
    risk = RiskScore(**app["risk_score"]) if app.get("risk_score") else RiskScore(score=0, risk_level=RiskLevel.LOW)

    explanation = await explain_risk(discrepancies, risk, lang=body.language)

    # Cache it
    app["explanation"] = explanation
    _APPS[app_id] = app

    # Optionally generate TTS
    audio_b64 = None
    if body.language.startswith("hi"):
        try:
            audio_b64 = await sarvam_client.text_to_speech(explanation, target_lang="hi-IN")
        except Exception:
            pass

    return ExplainResponse(explanation=explanation, language=body.language, audio_base64=audio_b64)


@router.post("/applications/{app_id}/decide")
async def decide_application(app_id: str, body: OfficerDecision):
    """Officer submits a decision on an application."""
    _ensure_seeded()
    app = _APPS.get(app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    status_map = {
        "approve": ApplicationStatus.APPROVED.value,
        "flag": ApplicationStatus.FLAGGED.value,
        "reject": ApplicationStatus.REJECTED.value,
    }
    app["status"] = status_map.get(body.action.value, app["status"])
    app["decision_action"] = body.action.value
    app["decision_reason"] = body.reason
    _APPS[app_id] = app

    return {"status": "ok", "new_status": app["status"]}
