"""Ghost beneficiary detection — flags phantom applicants with no document trail."""

from __future__ import annotations

from app.models.schemas import AnomalyFinding, Severity


async def detect(
    app_id: str,
    declared: dict,
    connector_results: list,
    all_apps_store: dict[str, dict],
) -> list[AnomalyFinding]:
    """Detect ghost/phantom beneficiaries lacking real verification trails."""
    findings: list[AnomalyFinding] = []

    # Check if the app entry exists
    app = all_apps_store.get(app_id, {})
    docs = app.get("documents", [])

    # Signal 1: No documents submitted at all
    if not docs:
        findings.append(AnomalyFinding(
            anomaly_type="ghost_beneficiary_no_docs",
            description="Application has zero supporting documents — possible ghost beneficiary.",
            severity=Severity.HIGH,
            contributing_score=20,
            evidence=f"app_id={app_id}, document_count=0",
        ))
        return findings  # Everything below is moot without docs

    # Signal 2: Documents present but no meaningful extraction
    extracted_count = sum(
        1 for d in docs if d.get("extracted") and any(
            v for k, v in d["extracted"].items() if k != "confidence" and v
        )
    )
    if extracted_count == 0:
        findings.append(AnomalyFinding(
            anomaly_type="ghost_beneficiary_empty_extraction",
            description="All submitted documents have empty or unreadable extraction results.",
            severity=Severity.HIGH,
            contributing_score=18,
            evidence=f"app_id={app_id}, docs={len(docs)}, extracted=0",
        ))

    # Signal 3: Aadhaar connector returned no record at all
    aadhaar_result = None
    for cr in connector_results:
        if cr.source_name == "aadhaar_verification":
            aadhaar_result = cr
            break

    if aadhaar_result and not aadhaar_result.data:
        findings.append(AnomalyFinding(
            anomaly_type="ghost_beneficiary_no_aadhaar_record",
            description="Aadhaar verification returned no record for the declared identity.",
            severity=Severity.HIGH,
            contributing_score=15,
            evidence=f"app_id={app_id}, aadhaar connector returned empty data",
        ))

    # Signal 4: Name declared but no two documents agree on full_name
    doc_names = []
    for d in docs:
        ext = d.get("extracted", {})
        name = ext.get("full_name", "")
        if name:
            doc_names.append(name.strip().lower())
    if len(doc_names) >= 2:
        unique_names = set(doc_names)
        if len(unique_names) == len(doc_names):
            # Every document has a different name — suspicious
            findings.append(AnomalyFinding(
                anomaly_type="ghost_beneficiary_name_fragmentation",
                description="No two documents agree on the beneficiary's full name.",
                severity=Severity.MEDIUM,
                contributing_score=10,
                evidence=f"app_id={app_id}, unique_names={len(unique_names)}",
            ))

    return findings
