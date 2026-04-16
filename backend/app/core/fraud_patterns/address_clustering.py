"""Address clustering detection — unusual concentration of applicants at one address."""

from __future__ import annotations

from app.models.schemas import AnomalyFinding, Severity

_CLUSTER_THRESHOLD = 3  # Flag when this many+ distinct applicants share an address


async def detect(
    app_id: str,
    declared: dict,
    connector_results: list,
    all_apps_store: dict[str, dict],
) -> list[AnomalyFinding]:
    """Detect unusual clustering of applicants at the same address."""
    findings: list[AnomalyFinding] = []

    address = (declared.get("address") or "").strip().lower()
    if not address or len(address) < 10:
        return findings

    addr_tokens = _normalise_tokens(address)
    if len(addr_tokens) < 3:
        return findings

    cluster_ids: list[str] = []
    for oid, oapp in all_apps_store.items():
        if oid == app_id:
            continue
        od = oapp.get("declared", {})
        o_addr = (od.get("address") or "").strip().lower()
        if not o_addr:
            continue
        o_tokens = _normalise_tokens(o_addr)
        overlap = addr_tokens & o_tokens
        # Require strong overlap relative to the smaller token set
        min_len = min(len(addr_tokens), len(o_tokens))
        if min_len > 0 and len(overlap) / min_len >= 0.6:
            cluster_ids.append(oid)

    if len(cluster_ids) >= _CLUSTER_THRESHOLD:
        findings.append(AnomalyFinding(
            anomaly_type="address_cluster",
            description=(
                f"Address shared with {len(cluster_ids)} other applicant(s) — "
                f"possible address stuffing or shared-address fraud."
            ),
            severity=Severity.HIGH if len(cluster_ids) >= 5 else Severity.MEDIUM,
            contributing_score=12,
            evidence=f"cluster_size={len(cluster_ids) + 1}, linked_ids={cluster_ids[:5]}",
        ))

    return findings


def _normalise_tokens(address: str) -> set[str]:
    """Extract significant tokens from an address, ignoring common stopwords."""
    stop = {
        "road", "rd", "street", "st", "nagar", "colony", "village",
        "block", "india", "state", "district", "pin", "post", "office",
        "near", "opp", "behind", "the", "of", "and", "at",
    }
    return {t for t in address.split() if len(t) > 2 and t.rstrip(",.:;") not in stop}
