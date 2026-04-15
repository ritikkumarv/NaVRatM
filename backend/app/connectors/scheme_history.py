"""
Cross-scheme decision-trail connector (mock/synthetic).

Returns prior applications across government schemes, decision outcomes,
rejection reason codes, active benefit count, and duplicate flag.

Trust: 0.85 — synthetic; consolidates data from multiple scheme DBs.
"""

from __future__ import annotations
from typing import Any

from app.connectors import BaseConnector, ConnectorResult, SourceReliability

_TRUST = 0.85
_SOURCE = "scheme_history"

_PROFILES: dict[str, dict[str, Any]] = {
    "clean": {
        "prior_applications": [
            {"scheme": "PM-KISAN", "date": "2023-06-15", "status": "approved", "reason_code": None},
        ],
        "total_active_benefits": 1,
        "duplicate_flag": False,
    },
    "fraud-ring": {
        "prior_applications": [
            {"scheme": "PM-KISAN", "date": "2022-01-10", "status": "approved", "reason_code": None},
            {"scheme": "MGNREGS", "date": "2022-03-22", "status": "approved", "reason_code": None},
            {"scheme": "PMJAY", "date": "2022-05-14", "status": "approved", "reason_code": None},
            {"scheme": "Ujjwala", "date": "2023-01-05", "status": "approved", "reason_code": None},
            {"scheme": "PM-Awas", "date": "2023-08-20", "status": "rejected", "reason_code": "DUPLICATE_BENEFICIARY"},
            {"scheme": "PM-KISAN", "date": "2024-02-11", "status": "rejected", "reason_code": "IDENTITY_MISMATCH"},
        ],
        "total_active_benefits": 4,
        "duplicate_flag": True,
    },
    "income-mismatch": {
        "prior_applications": [
            {"scheme": "PM-KISAN", "date": "2023-02-18", "status": "approved", "reason_code": None},
            {"scheme": "PMJAY", "date": "2023-09-01", "status": "under_review", "reason_code": "INCOME_VERIFY_PENDING"},
        ],
        "total_active_benefits": 1,
        "duplicate_flag": False,
    },
    "deceased": {
        "prior_applications": [
            {"scheme": "PM-KISAN", "date": "2020-04-10", "status": "approved", "reason_code": None},
            {"scheme": "Old-Age-Pension", "date": "2021-07-01", "status": "approved", "reason_code": None},
            {"scheme": "PM-KISAN", "date": "2026-01-15", "status": "approved", "reason_code": None},  # post-death disbursement
        ],
        "total_active_benefits": 2,
        "duplicate_flag": False,
    },
}


def _resolve(entity_id: str) -> dict[str, Any] | None:
    eid = entity_id.lower()
    for prefix in _PROFILES:
        if eid.startswith(prefix):
            return _PROFILES[prefix]
    return None


class SchemeHistoryConnector(BaseConnector):
    name = _SOURCE

    async def fetch(self, entity_id: str, **kwargs: Any) -> ConnectorResult:
        profile = _resolve(entity_id)
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
                evidence_uri="https://services.india.gov.in",
            ),
        )
