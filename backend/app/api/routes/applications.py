"""Application & verification routes — the core API surface for officers."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.config import risk_band_for_score
from app.core import sarvam_client
from app.core.pipeline import process_application as run_pipeline
from app.data.seed_data import SEED_APPLICATIONS
from app.models.schemas import (
    ApplicationCreate,
    ApplicationListItem,
    ApplicationResponse,
    ApplicationStatus,
    CanonicalRiskProfile,
    DashboardStats,
    DeclaredValues,
    Discrepancy,
    ExplainRequest,
    ExplainResponse,
    ExtractedFields,
    OfficerDecision,
    RiskBand,
)

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["applications"])

# ────────────────────── In-memory store (hackathon speed) ──────────────────────
_APPS: dict[str, dict] = {}
_seeded = False


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_seeded() -> None:
    """Populate in-memory store from seed data on first access."""
    global _seeded
    if _seeded:
        return
    _seeded = True
    for seed in SEED_APPLICATIONS:
        app_id = seed["id"]
        score = seed.get("expected_score", 0)
        band = risk_band_for_score(score)
        risk_label = seed.get("expected_risk", band)

        if risk_label in ("high", "critical"):
            status = ApplicationStatus.FLAGGED.value
        elif risk_label == "medium":
            status = ApplicationStatus.UNDER_REVIEW.value
        else:
            status = ApplicationStatus.PENDING.value

        _APPS[app_id] = {
            "id": app_id,
            "declared": seed["declared"],
            "status": status,
            "risk_score": score,
            "risk_band": risk_label,
            "risk_factors": [],
            "discrepancies": [],
            "anomalies": [],
            "network_flags": [],
            "explanation": None,
            "documents": seed.get("documents", []),
            "created_at": "2025-04-15T10:00:00Z",
            "updated_at": "2025-04-15T10:00:00Z",
        }


# ────────────────────── Dashboard stats ──────────────────────


@router.get("/stats", response_model=DashboardStats)
async def get_stats():
    _ensure_seeded()
    apps = list(_APPS.values())
    scores = [a["risk_score"] for a in apps if a.get("risk_score") is not None]
    return DashboardStats(
        total_applications=len(apps),
        pending=sum(1 for a in apps if a["status"] == "pending"),
        under_review=sum(1 for a in apps if a["status"] == "under_review"),
        approved=sum(1 for a in apps if a["status"] == "approved"),
        flagged=sum(1 for a in apps if a["status"] == "flagged"),
        rejected=sum(1 for a in apps if a["status"] == "rejected"),
        escalated=sum(1 for a in apps if a["status"] == "escalated"),
        avg_risk_score=sum(scores) / max(len(scores), 1),
        high_risk_count=sum(
            1 for a in apps if a.get("risk_band") in ("high", "critical")
        ),
    )


# ────────────────────── List / Detail ──────────────────────


@router.get("/applications", response_model=list[ApplicationListItem])
async def list_applications(
    status: str | None = None,
    risk_band: str | None = None,
    scheme: str | None = None,
    sort_by: str = "risk_score",
    sort_order: str = "desc",
):
    _ensure_seeded()
    apps = list(_APPS.values())

    if status:
        apps = [a for a in apps if a["status"] == status]
    if risk_band:
        apps = [a for a in apps if a.get("risk_band") == risk_band]
    if scheme:
        apps = [a for a in apps if a["declared"].get("scheme", "").lower() == scheme.lower()]

    def _sort_key(a: dict):
        if sort_by == "risk_score":
            return a.get("risk_score") or 0
        if sort_by == "name":
            return a["declared"].get("full_name", "")
        if sort_by == "created_at":
            return a.get("created_at", "")
        return 0

    apps.sort(key=_sort_key, reverse=(sort_order == "desc"))

    return [
        ApplicationListItem(
            id=a["id"],
            applicant_name=a["declared"].get("full_name", "Unknown"),
            scheme=a["declared"].get("scheme", "Unknown"),
            status=a["status"],
            risk_score=a.get("risk_score"),
            risk_band=a.get("risk_band"),
            created_at=a.get("created_at", ""),
        )
        for a in apps
    ]


@router.get("/applications/{app_id}", response_model=ApplicationResponse)
async def get_application(app_id: str):
    _ensure_seeded()
    app = _APPS.get(app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    profile = CanonicalRiskProfile(
        case_id=app["id"],
        risk_score=app.get("risk_score") or 0,
        risk_band=app.get("risk_band") or "low",
        factors=app.get("risk_factors", []),
        anomalies=app.get("anomalies", []),
        network_flags=app.get("network_flags", []),
    )

    return ApplicationResponse(
        id=app["id"],
        declared=DeclaredValues(**app["declared"]),
        status=app["status"],
        risk_score=app.get("risk_score"),
        risk_band=app.get("risk_band"),
        risk_profile=profile,
        discrepancies=[Discrepancy(**d) for d in app.get("discrepancies", [])],
        explanation=app.get("explanation"),
        created_at=app.get("created_at", ""),
        updated_at=app.get("updated_at", ""),
    )


# ────────────────────── Create ──────────────────────


@router.post("/applications", response_model=ApplicationResponse)
async def create_application(body: ApplicationCreate):
    _ensure_seeded()
    app_id = f"APP-{str(uuid.uuid4())[:4].upper()}"
    now = _now_iso()
    _APPS[app_id] = {
        "id": app_id,
        "declared": body.declared.model_dump(),
        "status": ApplicationStatus.PENDING.value,
        "risk_score": None,
        "risk_band": None,
        "risk_factors": [],
        "discrepancies": [],
        "anomalies": [],
        "network_flags": [],
        "explanation": None,
        "documents": body.documents,
        "created_at": now,
        "updated_at": now,
    }
    return ApplicationResponse(id=app_id, declared=body.declared, created_at=now, updated_at=now)


# ────────────────────── Process (Sprint 2 pipeline) ──────────────────────


@router.post("/applications/{app_id}/process")
async def process_application(app_id: str):
    """Trigger the fraud-detection pipeline and store the resulting risk profile."""
    _ensure_seeded()
    app = _APPS.get(app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    app["status"] = ApplicationStatus.UNDER_REVIEW.value
    app["updated_at"] = _now_iso()

    declared = DeclaredValues(**app["declared"])

    # Build extracted_docs from the stored documents
    extracted_docs: list[tuple[str, ExtractedFields]] = []
    for doc in app.get("documents", []):
        ext = doc.get("extracted")
        if ext:
            source = doc.get("source", doc.get("type", "unknown"))
            try:
                fields = ExtractedFields(**ext)
            except Exception:
                continue
            extracted_docs.append((source, fields))

    profile = await run_pipeline(app_id, declared, extracted_docs)

    # Persist profile data back into in-memory store
    app["risk_score"] = profile.risk_score
    app["risk_band"] = profile.risk_band.value if hasattr(profile.risk_band, "value") else profile.risk_band
    app["risk_factors"] = [f.model_dump() for f in profile.factors]
    app["anomalies"] = [a.model_dump() for a in profile.anomalies]
    app["network_flags"] = [n.model_dump() for n in profile.network_flags]
    app["updated_at"] = _now_iso()

    # Update status based on recommended action
    action_status = {
        "approve": ApplicationStatus.APPROVED.value,
        "manual_review": ApplicationStatus.UNDER_REVIEW.value,
        "escalate": ApplicationStatus.ESCALATED.value,
    }
    app["status"] = action_status.get(profile.recommended_action, ApplicationStatus.UNDER_REVIEW.value)

    return profile.model_dump()


# ────────────────────── Decide ──────────────────────


@router.post("/applications/{app_id}/decide")
async def decide_application(app_id: str, body: OfficerDecision):
    _ensure_seeded()
    app = _APPS.get(app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    status_map = {
        "approve": ApplicationStatus.APPROVED.value,
        "flag": ApplicationStatus.FLAGGED.value,
        "reject": ApplicationStatus.REJECTED.value,
        "escalate": ApplicationStatus.ESCALATED.value,
    }
    app["status"] = status_map.get(body.action.value, app["status"])
    app["decision_action"] = body.action.value
    app["decision_reason"] = body.reason
    app["updated_at"] = _now_iso()
    return {"status": "ok", "new_status": app["status"]}


# ────────────────────── Explain ──────────────────────


@router.post("/applications/{app_id}/explain", response_model=ExplainResponse)
async def explain_application(app_id: str, body: ExplainRequest = ExplainRequest()):
    _ensure_seeded()
    app = _APPS.get(app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    score = app.get("risk_score") or 0
    band = app.get("risk_band") or "low"
    discs = app.get("discrepancies", [])

    prompt = (
        "You are a fraud detection assistant for Indian welfare schemes.\n"
        f"Application {app_id} received risk score {score}/100 ({band} risk).\n"
        f"Discrepancies: {discs}\n\n"
        "Write a concise 3-4 sentence explanation for an officer."
    )

    try:
        explanation = await sarvam_client.chat(
            messages=[{"role": "user", "content": prompt}]
        )
    except Exception:
        explanation = (
            f"Application {app_id} has a risk score of {score}/100 ({band}). "
            f"Found {len(discs)} discrepancies across submitted documents."
        )

    app["explanation"] = explanation

    # TTS if Hindi requested
    audio_b64 = None
    if body.language.startswith("hi"):
        try:
            translated = await sarvam_client.translate_text(
                explanation, "en-IN", "hi-IN"
            )
            audio_b64 = await sarvam_client.tts(translated, target_language_code="hi-IN")
        except Exception:
            pass

    return ExplainResponse(
        explanation=explanation, language=body.language, audio_base64=audio_b64
    )
