"""Risk scoring engine — weighted rule-based scoring with factor breakdown."""

from __future__ import annotations
from app.models.schemas import Discrepancy, RiskScore, RiskFactor, RiskLevel, Severity


# ────────────────────── Scoring rules ──────────────────────

RULES = {
    "dob_mismatch":       {"weight": 25, "desc": "Date of birth mismatch across documents"},
    "income_deviation":   {"weight": 20, "desc": "Declared income deviates significantly from bank records"},
    "name_mismatch":      {"weight": 20, "desc": "Name mismatch detected (fuzzy match below threshold)"},
    "address_mismatch":   {"weight": 10, "desc": "Address inconsistency across documents"},
    "gender_mismatch":    {"weight": 10, "desc": "Gender mismatch between declaration and documents"},
    "phone_mismatch":     {"weight": 5,  "desc": "Phone number inconsistency"},
    "duplicate_aadhaar":  {"weight": 30, "desc": "Duplicate Aadhaar number found in system"},
    "missing_docs":       {"weight": 15, "desc": "Required supporting documents not submitted"},
    "age_ineligible":     {"weight": 15, "desc": "Applicant age outside scheme eligibility range"},
    "multi_scheme_claim": {"weight": 20, "desc": "Multiple scheme claims from same household"},
}

FIELD_TO_RULE = {
    "date_of_birth": "dob_mismatch",
    "income_monthly": "income_deviation",
    "full_name": "name_mismatch",
    "address": "address_mismatch",
    "gender": "gender_mismatch",
    "phone": "phone_mismatch",
}

SEVERITY_MULTIPLIER = {
    Severity.HIGH: 1.0,
    Severity.MEDIUM: 0.6,
    Severity.LOW: 0.3,
}


def _risk_level(score: int) -> RiskLevel:
    if score <= 20:
        return RiskLevel.LOW
    elif score <= 50:
        return RiskLevel.MEDIUM
    elif score <= 75:
        return RiskLevel.HIGH
    return RiskLevel.CRITICAL


def _recommended_action(level: RiskLevel) -> str:
    return {
        RiskLevel.LOW: "approve",
        RiskLevel.MEDIUM: "manual_review",
        RiskLevel.HIGH: "manual_review",
        RiskLevel.CRITICAL: "reject",
    }[level]


def calculate_risk(
    discrepancies: list[Discrepancy],
    num_documents: int = 1,
    duplicate_found: bool = False,
    missing_required_docs: bool = False,
) -> RiskScore:
    """Calculate risk score from discrepancies and contextual signals.

    Returns a RiskScore with 0-100 score, level, contributing factors, and action.
    """
    factors: list[RiskFactor] = []
    seen_rules: set[str] = set()
    total = 0

    # Score from discrepancies
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
            rule_id=rule_id,
            rule_name=disc.field.replace("_", " ").title(),
            points=points,
            description=f"{rule['desc']}. {disc.details}",
            confidence=disc.severity.value,
        ))

    # Contextual signals
    if duplicate_found and "duplicate_aadhaar" not in seen_rules:
        pts = RULES["duplicate_aadhaar"]["weight"]
        total += pts
        factors.append(RiskFactor(
            rule_id="duplicate_aadhaar",
            rule_name="Duplicate Aadhaar",
            points=pts,
            description=RULES["duplicate_aadhaar"]["desc"],
            confidence="high",
        ))

    if missing_required_docs and "missing_docs" not in seen_rules:
        pts = RULES["missing_docs"]["weight"]
        total += pts
        factors.append(RiskFactor(
            rule_id="missing_docs",
            rule_name="Missing Documents",
            points=pts,
            description=RULES["missing_docs"]["desc"],
            confidence="medium",
        ))

    # Cap at 100
    score = min(total, 100)
    level = _risk_level(score)

    # Sort factors by points descending
    factors.sort(key=lambda f: f.points, reverse=True)

    return RiskScore(
        score=score,
        risk_level=level,
        factors=factors,
        recommended_action=_recommended_action(level),
    )
