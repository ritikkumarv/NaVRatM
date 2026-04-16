"""Anomaly detection engine — orchestrates fraud patterns and network analysis."""

from __future__ import annotations

import logging

from app.core.fraud_patterns import run_all as run_all_patterns
from app.models.schemas import AnomalyFinding, NetworkFlag, Severity

log = logging.getLogger(__name__)

# Network flag bonus scores
_NETWORK_SCORES: dict[str, int] = {
    "shared_bank_account": 15,
    "address_cluster": 10,
    "phone_ring": 10,
}


async def detect_anomalies(
    app_id: str,
    declared: dict,
    extracted_docs: list,
    connector_results: list,
    all_apps_store: dict[str, dict],
) -> tuple[list[AnomalyFinding], list[NetworkFlag]]:
    """Run all fraud pattern detectors and derive network flags.

    Returns:
        (anomaly_findings, network_flags) — ready for risk score aggregation.
    """
    # Run all registered pattern detectors in parallel
    findings = await run_all_patterns(
        app_id, declared, connector_results, all_apps_store,
    )

    # Derive network flags from cross-app patterns
    network_flags = _derive_network_flags(findings, declared, all_apps_store, app_id)

    log.info(
        "Anomaly detection complete for app=%s: %d findings, %d network flags",
        app_id, len(findings), len(network_flags),
    )
    return findings, network_flags


def _derive_network_flags(
    findings: list[AnomalyFinding],
    declared: dict,
    all_apps_store: dict[str, dict],
    app_id: str,
) -> list[NetworkFlag]:
    """Generate NetworkFlag objects from pattern findings and cross-app analysis."""
    flags: list[NetworkFlag] = []
    seen: set[str] = set()

    for f in findings:
        # Shared bank account network
        if f.anomaly_type == "duplicate_identity_shared_bank" and "shared_bank_account" not in seen:
            seen.add("shared_bank_account")
            linked = _extract_ids_from_evidence(f.evidence)
            flags.append(NetworkFlag(
                flag_type="shared_bank_account",
                description=f.description,
                linked_entity_ids=linked,
                confidence=0.85,
            ))

        # Phone ring
        if f.anomaly_type == "duplicate_identity_shared_phone" and "phone_ring" not in seen:
            seen.add("phone_ring")
            linked = _extract_ids_from_evidence(f.evidence)
            flags.append(NetworkFlag(
                flag_type="phone_ring",
                description=f.description,
                linked_entity_ids=linked,
                confidence=0.80,
            ))

        # Address cluster
        if f.anomaly_type == "address_cluster" and "address_cluster" not in seen:
            seen.add("address_cluster")
            linked = _extract_ids_from_evidence(f.evidence)
            flags.append(NetworkFlag(
                flag_type="address_cluster",
                description=f.description,
                linked_entity_ids=linked,
                confidence=0.75,
            ))

        # Income ring
        if f.anomaly_type == "income_inflation_ring" and "income_ring" not in seen:
            seen.add("income_ring")
            linked = _extract_ids_from_evidence(f.evidence)
            flags.append(NetworkFlag(
                flag_type="income_ring",
                description=f.description,
                linked_entity_ids=linked,
                confidence=0.70,
            ))

    return flags


def _extract_ids_from_evidence(evidence: str) -> list[str]:
    """Extract app IDs from evidence strings like 'linked_ids=[APP-007, APP-008]'."""
    import re
    match = re.search(r"linked_ids=\[([^\]]*)\]", evidence)
    if not match:
        return []
    raw = match.group(1)
    ids = [s.strip().strip("'\"") for s in raw.split(",") if s.strip()]
    return ids
