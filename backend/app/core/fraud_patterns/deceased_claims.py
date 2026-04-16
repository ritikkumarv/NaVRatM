"""Deceased claims detection — flag applications matched to death registry."""

from __future__ import annotations

from app.models.schemas import AnomalyFinding, Severity


async def detect(
    app_id: str,
    declared: dict,
    connector_results: list,
    all_apps_store: dict[str, dict],
) -> list[AnomalyFinding]:
    """Flag applications where the beneficiary is matched in the death registry."""
    findings: list[AnomalyFinding] = []

    dr = None
    for cr in connector_results:
        if cr.source_name == "death_registry":
            dr = cr
            break

    if not dr or not dr.data:
        return findings

    if dr.data.get("is_deceased_match"):
        registry_date = dr.data.get("registry_date", "unknown")
        confidence = dr.data.get("match_confidence", 0.0)
        severity = Severity.HIGH if confidence >= 0.7 else Severity.MEDIUM

        findings.append(AnomalyFinding(
            anomaly_type="deceased_beneficiary",
            description=(
                f"Applicant matched against death registry "
                f"(date: {registry_date}, confidence: {confidence:.0%})."
            ),
            severity=severity,
            contributing_score=25,
            evidence=f"registry_date={registry_date}, confidence={confidence}",
        ))

        # Additional signal: application filed after death date
        if registry_date and registry_date != "unknown":
            app_entry = all_apps_store.get(app_id, {})
            created = app_entry.get("created_at", "")
            if created and registry_date < created[:10]:
                findings.append(AnomalyFinding(
                    anomaly_type="deceased_post_mortem_filing",
                    description=(
                        f"Application filed after death registry date ({registry_date})."
                    ),
                    severity=Severity.HIGH,
                    contributing_score=20,
                    evidence=f"death_date={registry_date}, filed={created[:10]}",
                ))

    return findings
