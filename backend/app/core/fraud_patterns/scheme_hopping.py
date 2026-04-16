"""Scheme hopping detection — same beneficiary across multiple schemes with inconsistent data."""

from __future__ import annotations

from app.models.schemas import AnomalyFinding, Severity


async def detect(
    app_id: str,
    declared: dict,
    connector_results: list,
    all_apps_store: dict[str, dict],
) -> list[AnomalyFinding]:
    """Flag same beneficiary applying to multiple schemes with data inconsistencies."""
    findings: list[AnomalyFinding] = []

    name = (declared.get("full_name") or "").strip().lower()
    aadhaar = (declared.get("aadhaar_masked") or "").strip()
    scheme = (declared.get("scheme") or "").strip().lower()

    if not name and not aadhaar:
        return findings

    other_schemes: list[dict] = []
    for oid, oapp in all_apps_store.items():
        if oid == app_id:
            continue
        od = oapp.get("declared", {})
        o_name = (od.get("full_name") or "").strip().lower()
        o_aadhaar = (od.get("aadhaar_masked") or "").strip()
        o_scheme = (od.get("scheme") or "").strip().lower()

        # Match by aadhaar or exact name
        matched = False
        if aadhaar and o_aadhaar and aadhaar == o_aadhaar:
            matched = True
        elif name and o_name and name == o_name:
            matched = True

        if matched and o_scheme and o_scheme != scheme:
            other_schemes.append({"id": oid, "scheme": o_scheme, "declared": od})

    if not other_schemes:
        # Also check connector: scheme_history might flag duplicates
        sh = None
        for cr in connector_results:
            if cr.source_name == "scheme_history":
                sh = cr
                break
        if sh and sh.data.get("duplicate_flag"):
            prev = sh.data.get("previous_schemes", [])
            findings.append(AnomalyFinding(
                anomaly_type="scheme_hopping_connector",
                description=(
                    f"Scheme history connector flagged duplicate enrolment "
                    f"across {len(prev)} scheme(s)."
                ),
                severity=Severity.MEDIUM,
                contributing_score=12,
                evidence=f"previous_schemes={prev[:5]}",
            ))
        return findings

    # Found same identity in other schemes — check for inconsistencies
    findings.append(AnomalyFinding(
        anomaly_type="scheme_hopping_multi_scheme",
        description=(
            f"Beneficiary found in {len(other_schemes)} other scheme(s): "
            f"{', '.join(s['scheme'] for s in other_schemes[:3])}."
        ),
        severity=Severity.MEDIUM,
        contributing_score=10,
        evidence=f"other_app_ids={[s['id'] for s in other_schemes[:5]]}",
    ))

    # Check for inconsistent data across schemes
    inconsistencies = []
    for other in other_schemes:
        od = other["declared"]
        if declared.get("dob") and od.get("dob") and declared["dob"] != od["dob"]:
            inconsistencies.append(f"DOB mismatch with {other['id']}")
        d_inc = declared.get("income_monthly", 0) or 0
        o_inc = od.get("income_monthly", 0) or 0
        if d_inc > 0 and o_inc > 0 and abs(d_inc - o_inc) / max(d_inc, o_inc) > 0.5:
            inconsistencies.append(f"Income mismatch with {other['id']}")
        if declared.get("gender") and od.get("gender") and declared["gender"] != od["gender"]:
            inconsistencies.append(f"Gender mismatch with {other['id']}")

    if inconsistencies:
        findings.append(AnomalyFinding(
            anomaly_type="scheme_hopping_inconsistent_data",
            description=(
                f"Cross-scheme data inconsistencies: {'; '.join(inconsistencies[:5])}."
            ),
            severity=Severity.HIGH,
            contributing_score=15,
            evidence=f"inconsistencies={inconsistencies[:10]}",
        ))

    return findings
