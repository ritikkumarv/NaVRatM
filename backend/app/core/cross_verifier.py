"""Cross-verification engine — compares declared, extracted, and connector data."""

from __future__ import annotations

import logging
import re

from rapidfuzz import fuzz

from app.models.schemas import (
    DeclaredValues,
    Discrepancy,
    ExtractedFields,
    Severity,
)

log = logging.getLogger(__name__)

# ── Thresholds ───────────────────────────────────────────────────────────

NAME_MATCH_THRESHOLD = 85        # fuzzy ratio below this → flag
ADDRESS_MATCH_THRESHOLD = 50
INCOME_DEVIATION_THRESHOLD = 0.30  # 30 %


# ── String helpers ───────────────────────────────────────────────────────


def _fuzzy_score(a: str, b: str) -> float:
    """Normalised fuzzy match score 0–100."""
    if not a or not b:
        return 100.0  # can't compare if missing
    return fuzz.token_sort_ratio(a.lower().strip(), b.lower().strip())


def _normalise_name(name: str) -> str:
    """Basic Indian-name normalisation."""
    name = name.strip().lower()
    name = re.sub(r"\s+", " ", name)
    for prefix in ("shri", "smt", "mr", "mrs", "ms", "dr", "sh"):
        name = re.sub(rf"^{prefix}\.?\s*", "", name)
    return name.strip()


def _norm_date(d: str) -> str:
    d = d.strip()
    m = re.match(r"(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})", d)
    if m:
        return f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"
    return d


# ── Individual verifiers ─────────────────────────────────────────────────


def verify_name(
    declared: str, extracted: str, source: str, evidence_uri: str | None = None,
) -> Discrepancy | None:
    if not declared or not extracted:
        return None
    score = _fuzzy_score(_normalise_name(declared), _normalise_name(extracted))
    if score >= NAME_MATCH_THRESHOLD:
        return None
    severity = Severity.HIGH if score < 50 else Severity.MEDIUM
    return Discrepancy(
        field="full_name",
        declared_value=declared,
        extracted_value=extracted,
        source_document=source,
        severity=severity,
        match_score=score / 100.0,
        details=f"Name fuzzy match score: {score:.0f}% (threshold: {NAME_MATCH_THRESHOLD}%)",
        evidence_uri=evidence_uri,
    )


def verify_dob(
    declared: str, extracted: str, source: str, evidence_uri: str | None = None,
) -> Discrepancy | None:
    if not declared or not extracted:
        return None
    d1, d2 = _norm_date(declared), _norm_date(extracted)
    if d1 == d2:
        return None
    return Discrepancy(
        field="dob",
        declared_value=declared,
        extracted_value=extracted,
        source_document=source,
        severity=Severity.HIGH,
        match_score=0.0,
        details=f"DOB mismatch: declared '{declared}' vs extracted '{extracted}' from {source}",
        evidence_uri=evidence_uri,
    )


def verify_income(
    declared: float,
    extracted: float,
    source: str,
    evidence_uri: str | None = None,
) -> Discrepancy | None:
    if declared <= 0 or extracted <= 0:
        return None
    deviation = abs(declared - extracted) / max(declared, extracted)
    if deviation <= INCOME_DEVIATION_THRESHOLD:
        return None
    severity = Severity.HIGH if deviation > 0.8 else Severity.MEDIUM
    return Discrepancy(
        field="income_monthly",
        declared_value=f"₹{declared:,.0f}",
        extracted_value=f"₹{extracted:,.0f}",
        source_document=source,
        severity=severity,
        match_score=round(1.0 - deviation, 3),
        details=f"Income deviation: {deviation * 100:.0f}% ({source} shows ₹{extracted:,.0f} vs declared ₹{declared:,.0f})",
        evidence_uri=evidence_uri,
    )


def verify_address(
    declared: str, extracted: str, source: str, evidence_uri: str | None = None,
) -> Discrepancy | None:
    if not declared or not extracted:
        return None
    score = _fuzzy_score(declared, extracted)
    if score >= ADDRESS_MATCH_THRESHOLD:
        return None
    return Discrepancy(
        field="address",
        declared_value=declared,
        extracted_value=extracted,
        source_document=source,
        severity=Severity.MEDIUM,
        match_score=score / 100.0,
        details=f"Address fuzzy match: {score:.0f}% (threshold: {ADDRESS_MATCH_THRESHOLD}%)",
        evidence_uri=evidence_uri,
    )


def verify_gender(
    declared: str, extracted: str, source: str, evidence_uri: str | None = None,
) -> Discrepancy | None:
    if not declared or not extracted:
        return None
    d, e = declared.strip().lower(), extracted.strip().lower()
    if d == e or d[0] == e[0]:
        return None
    return Discrepancy(
        field="gender",
        declared_value=declared,
        extracted_value=extracted,
        source_document=source,
        severity=Severity.HIGH,
        match_score=0.0,
        details=f"Gender mismatch: '{declared}' vs '{extracted}'",
        evidence_uri=evidence_uri,
    )


def verify_phone(
    declared: str, extracted: str, source: str, evidence_uri: str | None = None,
) -> Discrepancy | None:
    if not declared or not extracted:
        return None
    d = re.sub(r"\D", "", declared)
    e = re.sub(r"\D", "", extracted)
    if d == e or d[-4:] == e[-4:]:  # masked last-4 comparison
        return None
    return Discrepancy(
        field="phone",
        declared_value=declared,
        extracted_value=extracted,
        source_document=source,
        severity=Severity.LOW,
        match_score=0.0,
        details="Phone number mismatch",
        evidence_uri=evidence_uri,
    )


# ── Connector-derived verifiers ──────────────────────────────────────────


def _get_connector(name: str, results: list | None) -> object | None:
    """Find a ConnectorResult by source_name; returns None when missing."""
    if not results:
        return None
    for r in results:
        if r.source_name == name:
            return r
    return None


def _evidence(cr: object) -> str | None:
    """Extract evidence_uri from a ConnectorResult if available."""
    rel = getattr(cr, "reliability", None)
    if rel is None:
        return None
    return getattr(rel, "evidence_uri", None)


def _verify_connector_income(
    declared: DeclaredValues, results: list | None,
) -> Discrepancy | None:
    cr = _get_connector("pan_income_tax", results)
    if cr is None or not cr.data:
        return None
    assessed_annual = cr.data.get("assessed_annual_income", 0)
    if assessed_annual <= 0:
        return None
    assessed_monthly = assessed_annual / 12.0
    declared_monthly = declared.income_monthly
    if declared_monthly <= 0:
        return None
    deviation = abs(declared_monthly - assessed_monthly) / max(declared_monthly, assessed_monthly)
    if deviation <= INCOME_DEVIATION_THRESHOLD:
        return None
    severity = Severity.HIGH if deviation > 0.8 else Severity.MEDIUM
    return Discrepancy(
        field="income_monthly",
        declared_value=f"₹{declared_monthly:,.0f}",
        extracted_value=f"₹{assessed_monthly:,.0f} (PAN/AIS assessed)",
        source_document="pan_income_tax connector",
        severity=severity,
        match_score=round(1.0 - deviation, 3),
        details=(
            f"Income deviation vs PAN connector: {deviation * 100:.0f}%. "
            f"Assessed annual ₹{assessed_annual:,.0f} → monthly ₹{assessed_monthly:,.0f} "
            f"vs declared ₹{declared_monthly:,.0f}"
        ),
        evidence_uri=_evidence(cr),
    )


def _verify_connector_duplicate(results: list | None) -> Discrepancy | None:
    cr = _get_connector("scheme_history", results)
    if cr is None or not cr.data:
        return None
    if not cr.data.get("duplicate_flag"):
        return None
    return Discrepancy(
        field="duplicate_detected",
        declared_value="unique applicant",
        extracted_value="duplicate_flag=true",
        source_document="scheme_history connector",
        severity=Severity.HIGH,
        match_score=0.0,
        details="Scheme-history connector reports duplicate beneficiary flag",
        evidence_uri=_evidence(cr),
    )


def _verify_connector_deceased(results: list | None) -> Discrepancy | None:
    cr = _get_connector("death_registry", results)
    if cr is None or not cr.data:
        return None
    if not cr.data.get("is_deceased_match"):
        return None
    return Discrepancy(
        field="deceased_match",
        declared_value="alive",
        extracted_value="deceased (registry match)",
        source_document="death_registry connector",
        severity=Severity.HIGH,
        match_score=0.0,
        details=(
            f"Death-registry match with confidence "
            f"{cr.data.get('match_confidence', 'N/A')}, "
            f"registry date {cr.data.get('registry_date', 'N/A')}"
        ),
        evidence_uri=_evidence(cr),
    )


# ── Main entry point ────────────────────────────────────────────────────


def cross_verify(
    declared: DeclaredValues,
    extracted_docs: list[tuple[str, ExtractedFields]],
    connector_results: list | None = None,
) -> list[Discrepancy]:
    """Run all verification checks across declared, document, and connector data.

    Args:
        declared: Applicant's self-declared values.
        extracted_docs: List of ``(doc_source_name, ExtractedFields)`` tuples.
        connector_results: Optional list of ``ConnectorResult`` from enrichment connectors.

    Returns:
        Ordered list of discovered discrepancies.
    """
    discrepancies: list[Discrepancy] = []

    # ── Document-vs-declared checks ──────────────────────────────────
    for source, fields in extracted_docs:
        if d := verify_name(declared.full_name, fields.full_name, source):
            discrepancies.append(d)
        if d := verify_dob(declared.dob, fields.dob, source):
            discrepancies.append(d)
        if d := verify_income(declared.income_monthly, fields.income_monthly or 0, source):
            discrepancies.append(d)
        if d := verify_address(declared.address, fields.address, source):
            discrepancies.append(d)
        if d := verify_gender(declared.gender, fields.gender, source):
            discrepancies.append(d)
        if d := verify_phone(declared.phone_masked, fields.phone_masked, source):
            discrepancies.append(d)

    # ── Cross-document checks ────────────────────────────────────────
    if len(extracted_docs) >= 2:
        for i in range(len(extracted_docs)):
            for j in range(i + 1, len(extracted_docs)):
                src_i, fields_i = extracted_docs[i]
                src_j, fields_j = extracted_docs[j]
                if d := verify_dob(fields_i.dob, fields_j.dob, f"{src_i} vs {src_j}"):
                    d.details = f"DOB inconsistency between documents: {src_i} and {src_j}"
                    discrepancies.append(d)
                if d := verify_name(fields_i.full_name, fields_j.full_name, f"{src_i} vs {src_j}"):
                    d.details = f"Name inconsistency between documents: {src_i} and {src_j}"
                    discrepancies.append(d)

    # ── Connector-derived checks ─────────────────────────────────────
    if connector_results:
        if d := _verify_connector_income(declared, connector_results):
            discrepancies.append(d)
        if d := _verify_connector_duplicate(connector_results):
            discrepancies.append(d)
        if d := _verify_connector_deceased(connector_results):
            discrepancies.append(d)

    return discrepancies
