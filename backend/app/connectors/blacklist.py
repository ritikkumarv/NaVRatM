"""
Central blacklist / watchlist connector (mock/synthetic).

Returns blacklist status, entries with reason, date added, severity,
and source agency.

Trust: 0.95 — high-authority centralised list.
"""

from __future__ import annotations
from typing import Any

from app.connectors import BaseConnector, ConnectorResult, SourceReliability

_TRUST = 0.95
_SOURCE = "central_blacklist"

_PROFILES: dict[str, dict[str, Any]] = {
    "clean": {
        "is_blacklisted": False,
        "blacklist_entries": [],
    },
    "fraud-ring": {
        "is_blacklisted": True,
        "blacklist_entries": [
            {
                "reason": "Multiple fraudulent benefit claims using fabricated identities",
                "date_added": "2024-11-15",
                "severity": "high",
                "source_agency": "MoRD-Vigilance",
            },
            {
                "reason": "Linked to organised beneficiary duplication ring",
                "date_added": "2025-02-28",
                "severity": "critical",
                "source_agency": "CBI-ACB",
            },
        ],
    },
    "income-mismatch": {
        "is_blacklisted": False,
        "blacklist_entries": [],
    },
    "deceased": {
        "is_blacklisted": False,
        "blacklist_entries": [],
    },
}


def _resolve(entity_id: str) -> dict[str, Any] | None:
    eid = entity_id.lower()
    for prefix in _PROFILES:
        if eid.startswith(prefix):
            return _PROFILES[prefix]
    return None


class BlacklistConnector(BaseConnector):
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
