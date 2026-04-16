"""Pipeline orchestration — extraction → verification → scoring DAG."""

from __future__ import annotations

import asyncio
import hashlib
import logging

from app.connectors import boot_connectors, registry
from app.core.cross_verifier import cross_verify
from app.core.anomaly_detector import detect_anomalies
from app.core.risk_scorer import calculate_risk
from app.models.schemas import (
    CanonicalRiskProfile,
    DeclaredValues,
    ExtractedFields,
)

log = logging.getLogger(__name__)


def _derive_entity_id(declared: DeclaredValues) -> str:
    """Derive a stable entity ID from declared values.

    Prefers aadhaar_masked (last-4 is unique enough for mock routing);
    falls back to a SHA-256 hash of the full name.
    """
    if declared.aadhaar_masked:
        # Use the masked aadhaar suffix as a prefix hint for connector routing
        suffix = declared.aadhaar_masked.replace("-", "").replace("X", "")
        return f"clean-{suffix}" if suffix else f"clean-{declared.full_name[:8]}"
    # Fallback: deterministic hash of name
    h = hashlib.sha256(declared.full_name.lower().encode()).hexdigest()[:12]
    return f"clean-{h}"


async def _fetch_all_connectors(entity_id: str) -> list:
    """Fetch all registered connectors in parallel, tolerating individual failures."""
    boot_connectors()

    connectors = list(registry.all().values())
    if not connectors:
        log.warning("No connectors registered — skipping enrichment")
        return []

    tasks = [c.fetch(entity_id) for c in connectors]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    good: list = []
    for connector, result in zip(connectors, results):
        if isinstance(result, BaseException):
            log.warning(
                "Connector %s failed for entity %s: %s",
                connector.name, entity_id, result,
            )
        else:
            good.append(result)
    return good


async def process_application(
    app_id: str,
    declared: DeclaredValues,
    extracted_docs: list[tuple[str, ExtractedFields]],
    all_apps_store: dict[str, dict] | None = None,
) -> CanonicalRiskProfile:
    """Run the full fraud-detection pipeline.

    Steps:
        1. Derive entity_id from declared values.
        2. Fetch all enrichment connectors in parallel.
        3. Cross-verify declared vs extracted vs connector data.
        4. Run anomaly detection across all fraud patterns.
        5. Calculate risk score with factor breakdown + anomaly scores.
        6. Return CanonicalRiskProfile.
    """
    entity_id = _derive_entity_id(declared)
    log.info("Pipeline started for app=%s entity=%s", app_id, entity_id)

    # Step 2 — parallel connector fetch
    connector_results = await _fetch_all_connectors(entity_id)

    # Step 3 — cross-verification
    discrepancies = cross_verify(declared, extracted_docs, connector_results)
    log.info(
        "Cross-verify complete: %d discrepancies for app=%s",
        len(discrepancies), app_id,
    )

    # Step 4 — anomaly detection (needs all_apps_store for cross-app patterns)
    anomalies = []
    network_flags = []
    if all_apps_store is not None:
        anomalies, network_flags = await detect_anomalies(
            app_id,
            declared.model_dump(),
            extracted_docs,
            connector_results,
            all_apps_store,
        )
        log.info(
            "Anomaly detection complete: %d anomalies, %d network flags for app=%s",
            len(anomalies), len(network_flags), app_id,
        )

    # Step 5 — risk scoring (now includes anomaly + network scores)
    profile = calculate_risk(
        discrepancies,
        connector_results=connector_results,
        num_documents=len(extracted_docs),
        anomalies=anomalies,
        network_flags_input=network_flags,
    )

    # Stamp the entity ID onto the profile
    profile.beneficiary_entity_id = entity_id

    log.info(
        "Pipeline complete for app=%s: score=%d band=%s action=%s",
        app_id, profile.risk_score, profile.risk_band, profile.recommended_action,
    )
    return profile
