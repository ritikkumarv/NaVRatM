"""Duplicate / synthetic identity detection — shared phone, bank, address across apps."""

from __future__ import annotations

from app.models.schemas import AnomalyFinding, Severity


async def detect(
    app_id: str,
    declared: dict,
    connector_results: list,
    all_apps_store: dict[str, dict],
) -> list[AnomalyFinding]:
    """Detect duplicate or synthetic identities sharing PII across applications."""
    findings: list[AnomalyFinding] = []

    phone = (declared.get("phone_masked") or "").strip()
    bank = (declared.get("bank_account_masked") or "").strip()
    aadhaar = (declared.get("aadhaar_masked") or "").strip()
    name = (declared.get("full_name") or "").strip().lower()

    phone_matches: list[str] = []
    bank_matches: list[str] = []
    aadhaar_matches: list[str] = []

    for oid, oapp in all_apps_store.items():
        if oid == app_id:
            continue
        od = oapp.get("declared", {})

        # Shared phone
        if phone and phone == (od.get("phone_masked") or "").strip():
            o_name = (od.get("full_name") or "").strip().lower()
            if o_name != name:
                phone_matches.append(oid)

        # Shared bank account
        if bank and bank == (od.get("bank_account_masked") or "").strip():
            bank_matches.append(oid)

        # Shared aadhaar (should be unique per person)
        if aadhaar and aadhaar == (od.get("aadhaar_masked") or "").strip():
            o_name = (od.get("full_name") or "").strip().lower()
            if o_name != name:
                aadhaar_matches.append(oid)

    if phone_matches:
        findings.append(AnomalyFinding(
            anomaly_type="duplicate_identity_shared_phone",
            description=(
                f"Phone number shared with {len(phone_matches)} other application(s) "
                f"under different names."
            ),
            severity=Severity.HIGH if len(phone_matches) >= 2 else Severity.MEDIUM,
            contributing_score=12,
            evidence=f"linked_ids={phone_matches[:5]}",
        ))

    if bank_matches:
        findings.append(AnomalyFinding(
            anomaly_type="duplicate_identity_shared_bank",
            description=(
                f"Bank account shared with {len(bank_matches)} other application(s)."
            ),
            severity=Severity.HIGH,
            contributing_score=15,
            evidence=f"linked_ids={bank_matches[:5]}",
        ))

    if aadhaar_matches:
        findings.append(AnomalyFinding(
            anomaly_type="duplicate_identity_shared_aadhaar",
            description=(
                f"Aadhaar ID used by {len(aadhaar_matches)} other application(s) "
                f"with different names — possible synthetic identity."
            ),
            severity=Severity.HIGH,
            contributing_score=20,
            evidence=f"linked_ids={aadhaar_matches[:5]}",
        ))

    return findings
