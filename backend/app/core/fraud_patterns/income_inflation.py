"""Income inflation / under-reporting ring detection."""

from __future__ import annotations

from app.models.schemas import AnomalyFinding, Severity


_INCOME_THRESHOLD_LOW = 12000.0   # Monthly cap for many welfare schemes
_CLUSTER_MIN_SIZE = 3             # Minimum ring size to flag


async def detect(
    app_id: str,
    declared: dict,
    connector_results: list,
    all_apps_store: dict[str, dict],
) -> list[AnomalyFinding]:
    """Detect coordinated income under-reporting and inflation patterns."""
    findings: list[AnomalyFinding] = []

    declared_income = declared.get("income_monthly", 0.0) or 0.0

    # Signal 1: Connector-reported income much higher than declared
    pan_result = None
    for cr in connector_results:
        if cr.source_name == "pan_income":
            pan_result = cr
            break

    if pan_result and pan_result.data:
        reported = pan_result.data.get("last_filed_income_annual", 0)
        if reported:
            monthly_from_itr = reported / 12.0
            if declared_income > 0 and monthly_from_itr > declared_income * 2.5:
                findings.append(AnomalyFinding(
                    anomaly_type="income_inflation_itr_mismatch",
                    description=(
                        f"Declared monthly income ₹{declared_income:.0f} but ITR implies "
                        f"₹{monthly_from_itr:.0f}/month — {monthly_from_itr / max(declared_income, 1):.1f}x gap."
                    ),
                    severity=Severity.HIGH,
                    contributing_score=15,
                    evidence=f"declared={declared_income}, itr_monthly={monthly_from_itr:.0f}",
                ))

    # Signal 2: Income just under eligibility threshold (suspicious clustering)
    if 0 < declared_income <= _INCOME_THRESHOLD_LOW:
        address = (declared.get("address") or "").strip().lower()
        scheme = (declared.get("scheme") or "").strip().lower()
        if address:
            similar_apps = []
            for oid, oapp in all_apps_store.items():
                if oid == app_id:
                    continue
                od = oapp.get("declared", {})
                o_income = od.get("income_monthly", 0) or 0
                o_addr = (od.get("address") or "").strip().lower()
                o_scheme = (od.get("scheme") or "").strip().lower()
                if (
                    o_scheme == scheme
                    and 0 < o_income <= _INCOME_THRESHOLD_LOW
                    and _address_overlap(address, o_addr)
                ):
                    similar_apps.append(oid)

            if len(similar_apps) >= _CLUSTER_MIN_SIZE:
                findings.append(AnomalyFinding(
                    anomaly_type="income_inflation_ring",
                    description=(
                        f"Coordinated under-reporting ring: {len(similar_apps) + 1} applicants at "
                        f"similar address all declared income ≤ ₹{_INCOME_THRESHOLD_LOW:.0f} for {scheme}."
                    ),
                    severity=Severity.HIGH,
                    contributing_score=18,
                    evidence=f"ring_size={len(similar_apps) + 1}, linked_ids={similar_apps[:5]}",
                ))

    return findings


def _address_overlap(a: str, b: str) -> bool:
    """Quick heuristic: addresses share at least 3 significant tokens."""
    stop = {"road", "street", "nagar", "colony", "village", "block", "india", "state", "district"}
    tokens_a = {t for t in a.split() if len(t) > 2 and t not in stop}
    tokens_b = {t for t in b.split() if len(t) > 2 and t not in stop}
    if not tokens_a or not tokens_b:
        return False
    overlap = tokens_a & tokens_b
    return len(overlap) >= 3
