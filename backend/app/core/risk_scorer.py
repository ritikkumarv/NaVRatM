"""Risk scoring engine — weighted rule-based model with connector enrichment."""

from __future__ import annotations

import uuid
import logging

from app.config import risk_band_for_score
from app.models.schemas import (
    CanonicalRiskProfile,
    Discrepancy,
    NetworkFlag,
    RiskBand,
    RiskFactor,
    Severity,
)

log = logging.getLogger(__name__)

# ── Weighted rules ───────────────────────────────────────────────────────

RULES: dict[str, dict] = {
    "dob_mismatch":          {"weight": 25, "desc": "Date of birth mismatch across documents"},
    "income_deviation":      {"weight": 20, "desc": "Declared income deviates significantly from records"},
    "name_mismatch":         {"weight": 20, "desc": "Name mismatch detected (fuzzy match below threshold)"},
    "address_mismatch":      {"weight": 10, "desc": "Address inconsistency across documents"},
    "gender_mismatch":       {"weight": 10, "desc": "Gender mismatch between declaration and documents"},
    "phone_mismatch":        {"weight": 5,  "desc": "Phone number inconsistency"},
    "duplicate_detected":    {"weight": 30, "desc": "Duplicate beneficiary flagged by scheme history"},
    "missing_docs":          {"weight": 15, "desc": "Required supporting documents not submitted"},
    "blacklisted":           {"weight": 35, "desc": "Applicant appears on central blacklist"},
    "deceased_match":        {"weight": 40, "desc": "Applicant matched against death registry"},
    "bank_velocity_anomaly": {"weight": 25, "desc": "Bank account mapped to suspiciously many beneficiaries"},
    "scheme_hopping":        {"weight": 20, "desc": "Duplicate-flag from cross-scheme history"},
}

# Map discrepancy field → rule_id
FIELD_TO_RULE: dict[str, str] = {
    "dob":                "dob_mismatch",
    "income_monthly":     "income_deviation",
    "full_name":          "name_mismatch",
    "address":            "address_mismatch",
    "gender":             "gender_mismatch",
    "phone":              "phone_mismatch",
    "duplicate_detected": "duplicate_detected",
    "deceased_match":     "deceased_match",
}

SEVERITY_MULTIPLIER: dict[Severity, float] = {
    Severity.HIGH:   1.0,
    Severity.MEDIUM: 0.6,
    Severity.LOW:    0.3,
}


def _recommended_action(band: str) -> str:
    return {
        "low": "approve",
        "medium": "manual_review",
        "high": "manual_review",
        "critical": "escalate",
    }.get(band, "manual_review")


# ── Connector signal helpers ─────────────────────────────────────────────


def _get_connector(name: str, results: list | None) -> object | None:
    if not results:
        return None
    for r in results:
        if r.source_name == name:
            return r
    return None


def _evidence(cr: object) -> str:
    rel = getattr(cr, "reliability", None)
    if rel is None:
        return ""
    return getattr(rel, "evidence_uri", "") or ""


# ── Public API ───────────────────────────────────────────────────────────


def calculate_risk(
    discrepancies: list[Discrepancy],
    connector_results: list | None = None,
    num_documents: int = 1,
) -> CanonicalRiskProfile:
    """Compute risk score from discrepancies + connector signals.

    Returns a fully-populated ``CanonicalRiskProfile`` ready for the officer UI.
    """
    factors: list[RiskFactor] = []
    network_flags: list[NetworkFlag] = []
    seen_rules: set[str] = set()
    total = 0

    # ── 1. Score from document discrepancies ─────────────────────────
    for disc in discrepancies:
        rule_id = FIELD_TO_RULE.get(disc.field)
        if not rule_id or rule_id in seen_rules:
            continue
        seen_rules.add(rule_id)
        rule = RULES[rule_id]
        multiplier = SEVERITY_MULTIPLIER.get(disc.severity, 0.5)
        points = int(rule["weight"] * multiplier)
        total += points
        factors.append(RiskFactor(
            factor_id=rule_id,
            factor_name=disc.field.replace("_", " ").title(),
            points=points,
            max_points=rule["weight"],
            description=f"{rule['desc']}. {disc.details}",
            confidence=multiplier,
            source_ref=disc.evidence_uri or disc.source_document,
        ))

    # ── 2. Missing-docs signal ───────────────────────────────────────
    if num_documents < 2 and "missing_docs" not in seen_rules:
        pts = RULES["missing_docs"]["weight"]
        total += pts
        seen_rules.add("missing_docs")
        factors.append(RiskFactor(
            factor_id="missing_docs",
            factor_name="Missing Documents",
            points=pts,
            max_points=pts,
            description=RULES["missing_docs"]["desc"],
            confidence=0.8,
            source_ref="document_count_check",
        ))

    # ── 3. Connector-derived signals ─────────────────────────────────

    # Blacklist
    bl = _get_connector("central_blacklist", connector_results)
    if bl and bl.data.get("is_blacklisted") and "blacklisted" not in seen_rules:
        pts = RULES["blacklisted"]["weight"]
        total += pts
        seen_rules.add("blacklisted")
        factors.append(RiskFactor(
            factor_id="blacklisted",
            factor_name="Blacklisted Applicant",
            points=pts,
            max_points=pts,
            description=RULES["blacklisted"]["desc"],
            confidence=1.0,
            source_ref=_evidence(bl),
        ))

    # Death registry
    dr = _get_connector("death_registry", connector_results)
    if dr and dr.data.get("is_deceased_match") and "deceased_match" not in seen_rules:
        pts = RULES["deceased_match"]["weight"]
        total += pts
        seen_rules.add("deceased_match")
        factors.append(RiskFactor(
            factor_id="deceased_match",
            factor_name="Deceased Match",
            points=pts,
            max_points=pts,
            description=(
                f"{RULES['deceased_match']['desc']}. "
                f"Registry date: {dr.data.get('registry_date', 'N/A')}"
            ),
            confidence=dr.data.get("match_confidence", 0.9),
            source_ref=_evidence(dr),
        ))

    # Bank velocity anomaly
    bv = _get_connector("bank_velocity", connector_results)
    mapped_count = bv.data.get("mapped_beneficiary_count", 0) if bv and bv.data else 0
    if mapped_count > 3 and "bank_velocity_anomaly" not in seen_rules:
        pts = RULES["bank_velocity_anomaly"]["weight"]
        total += pts
        seen_rules.add("bank_velocity_anomaly")
        factors.append(RiskFactor(
            factor_id="bank_velocity_anomaly",
            factor_name="Bank Velocity Anomaly",
            points=pts,
            max_points=pts,
            description=(
                f"{RULES['bank_velocity_anomaly']['desc']}. "
                f"Mapped beneficiaries: {mapped_count}"
            ),
            confidence=0.9,
            source_ref=_evidence(bv),
        ))
        # Also add a network flag for shared accounts
        network_flags.append(NetworkFlag(
            flag_type="shared_bank_account",
            description=f"Bank account mapped to {mapped_count} beneficiaries",
            linked_entity_ids=[],  # Sprint 3 can enrich with actual IDs
            confidence=0.85,
        ))

    # Scheme hopping (duplicate flag from scheme_history)
    sh = _get_connector("scheme_history", connector_results)
    if sh and sh.data.get("duplicate_flag") and "scheme_hopping" not in seen_rules:
        pts = RULES["scheme_hopping"]["weight"]
        total += pts
        seen_rules.add("scheme_hopping")
        factors.append(RiskFactor(
            factor_id="scheme_hopping",
            factor_name="Scheme Hopping / Duplicate",
            points=pts,
            max_points=pts,
            description=RULES["scheme_hopping"]["desc"],
            confidence=0.85,
            source_ref=_evidence(sh),
        ))

    # ── 4. Finalise ──────────────────────────────────────────────────
    score = min(total, 100)
    band = risk_band_for_score(score)
    factors.sort(key=lambda f: f.points, reverse=True)

    return CanonicalRiskProfile(
        case_id=str(uuid.uuid4()),
        risk_score=score,
        risk_band=RiskBand(band),
        factors=factors,
        anomalies=[],           # Sprint 3 will populate
        network_flags=network_flags,
        recommended_action=_recommended_action(band),
        confidence=round(sum(f.confidence for f in factors) / max(len(factors), 1), 2),
    )
