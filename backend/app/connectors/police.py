"""
Police / crime-reference connector (mock/synthetic).

Returns pending-case flag, alert level, and case count.

Trust: 0.80 — access-restricted source.

⚠️  Access restricted by policy; role-gated.
Only authorised officer roles with clearance level ≥ 2 should invoke
this connector. The calling pipeline must enforce RBAC before passing
results to the UI or audit trail.
"""

from __future__ import annotations
from typing import Any

from app.connectors import BaseConnector, ConnectorResult, SourceReliability

_TRUST = 0.80
_SOURCE = "police_crime_ref"

_PROFILES: dict[str, dict[str, Any]] = {
    "clean": {
        "has_pending_cases": False,
        "alert_level": "none",
        "case_count": 0,
    },
    "fraud-ring": {
        "has_pending_cases": True,
        "alert_level": "high",
        "case_count": 3,
    },
    "income-mismatch": {
        "has_pending_cases": False,
        "alert_level": "none",
        "case_count": 0,
    },
    "deceased": {
        "has_pending_cases": False,
        "alert_level": "none",
        "case_count": 0,
    },
}


def _resolve(entity_id: str) -> dict[str, Any] | None:
    eid = entity_id.lower()
    for prefix in _PROFILES:
        if eid.startswith(prefix):
            return _PROFILES[prefix]
    return None


class PoliceConnector(BaseConnector):
    """Access restricted by policy; role-gated."""

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
                evidence_uri="https://ncrb.gov.in",
            ),
        )
