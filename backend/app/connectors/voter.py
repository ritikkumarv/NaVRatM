"""
Voter / ECI connector (mock/synthetic).

Returns voter-ID status, constituency, and registered address.

Privacy: Voter ID is masked (first 3 chars visible).
Trust: 0.70 — synthetic; address may be outdated.
"""

from __future__ import annotations
from typing import Any

from app.connectors import BaseConnector, ConnectorResult, SourceReliability

_TRUST = 0.70
_SOURCE = "voter_eci"

_PROFILES: dict[str, dict[str, Any]] = {
    "clean": {
        "voter_id_masked": "ABC****234",
        "constituency": "Varanasi",
        "registered_address": "Ward 12, Varanasi, Uttar Pradesh",
        "active_status": True,
    },
    "fraud-ring": {
        "voter_id_masked": "XYZ****891",
        "constituency": "Patna Sahib",
        "registered_address": "Ward 5, Patna, Bihar",
        "active_status": True,
    },
    "income-mismatch": {
        "voter_id_masked": "PQR****567",
        "constituency": "Lucknow",
        "registered_address": "Sector 21, Lucknow, Uttar Pradesh",
        "active_status": True,
    },
    "deceased": {
        "voter_id_masked": "DEF****112",
        "constituency": "Ranchi",
        "registered_address": "Morabadi, Ranchi, Jharkhand",
        "active_status": True,  # not yet purged — stale record
    },
}


def _resolve(entity_id: str) -> dict[str, Any] | None:
    eid = entity_id.lower()
    for prefix in _PROFILES:
        if eid.startswith(prefix):
            return _PROFILES[prefix]
    return None


class VoterConnector(BaseConnector):
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
                evidence_uri="https://eci.gov.in",
            ),
        )
