"""
Aadhaar-linked history connector (mock/synthetic).

Returns linked welfare schemes, application history, rejection reasons,
and linked services for a given entity.

Privacy: Aadhaar numbers are never included in output.
"""

from __future__ import annotations
from typing import Any

from app.connectors import BaseConnector, ConnectorResult, SourceReliability

_TRUST = 0.85
_SOURCE = "aadhaar_linked_history"

# ── Mock profiles keyed by entity-id prefix ──────────────────────────

_PROFILES: dict[str, dict[str, Any]] = {
    "clean": {
        "linked_schemes": ["PM-KISAN"],
        "application_history": [
            {"scheme": "PM-KISAN", "applied_date": "2023-06-15", "status": "approved", "reason_code": None},
        ],
        "rejection_reasons": [],
        "linked_services": ["LPG-Ujjwala"],
    },
    "fraud-ring": {
        "linked_schemes": ["PM-KISAN", "MGNREGS", "PMJAY", "Ujjwala", "PM-Awas"],
        "application_history": [
            {"scheme": "PM-KISAN", "applied_date": "2022-01-10", "status": "approved", "reason_code": None},
            {"scheme": "MGNREGS", "applied_date": "2022-03-22", "status": "approved", "reason_code": None},
            {"scheme": "PMJAY", "applied_date": "2022-05-14", "status": "approved", "reason_code": None},
            {"scheme": "Ujjwala", "applied_date": "2023-01-05", "status": "approved", "reason_code": None},
            {"scheme": "PM-Awas", "applied_date": "2023-08-20", "status": "flagged", "reason_code": "DUPLICATE_BENEFICIARY"},
        ],
        "rejection_reasons": ["DUPLICATE_BENEFICIARY"],
        "linked_services": ["LPG-Ujjwala", "Banking-PMJDY", "Insurance-PMSBY"],
    },
    "income-mismatch": {
        "linked_schemes": ["PM-KISAN", "PMJAY"],
        "application_history": [
            {"scheme": "PM-KISAN", "applied_date": "2023-02-18", "status": "approved", "reason_code": None},
            {"scheme": "PMJAY", "applied_date": "2023-09-01", "status": "under_review", "reason_code": "INCOME_VERIFY_PENDING"},
        ],
        "rejection_reasons": [],
        "linked_services": ["Banking-PMJDY"],
    },
    "deceased": {
        "linked_schemes": ["PM-KISAN", "Old-Age-Pension"],
        "application_history": [
            {"scheme": "PM-KISAN", "applied_date": "2020-04-10", "status": "approved", "reason_code": None},
            {"scheme": "Old-Age-Pension", "applied_date": "2021-07-01", "status": "approved", "reason_code": None},
        ],
        "rejection_reasons": [],
        "linked_services": ["LPG-Ujjwala"],
    },
}


def _resolve_profile(entity_id: str) -> dict[str, Any] | None:
    eid = entity_id.lower()
    for prefix in _PROFILES:
        if eid.startswith(prefix):
            return _PROFILES[prefix]
    return None


class AadhaarConnector(BaseConnector):
    name = _SOURCE

    async def fetch(self, entity_id: str, **kwargs: Any) -> ConnectorResult:
        profile = _resolve_profile(entity_id)
        if profile is None:
            return self._empty()

        return ConnectorResult(
            source_name=self.name,
            data=profile,
            reliability=SourceReliability(
                source_name=self.name,
                source_trust_score=_TRUST,
                last_updated_at=self._now_iso(),
                access_mode="synthetic",
                evidence_uri="https://uidai.gov.in",
            ),
        )
