"""Fraud pattern registry — discovers and runs all pattern detectors."""

from __future__ import annotations

import asyncio
import logging
from typing import Callable, Awaitable

from app.models.schemas import AnomalyFinding

log = logging.getLogger(__name__)

# Type alias for a pattern detect function
PatternDetector = Callable[
    [str, dict, list, dict[str, dict]],
    Awaitable[list[AnomalyFinding]],
]

# Registry of all pattern modules
_PATTERNS: dict[str, PatternDetector] = {}


def register(name: str, fn: PatternDetector) -> None:
    """Register a fraud pattern detector by name."""
    _PATTERNS[name] = fn
    log.debug("Registered fraud pattern: %s", name)


def _auto_register() -> None:
    """Import all built-in pattern modules and register their detect() functions."""
    from app.core.fraud_patterns import (
        ghost_beneficiary,
        income_inflation,
        duplicate_identity,
        deceased_claims,
        scheme_hopping,
        address_clustering,
    )
    for name, mod in [
        ("ghost_beneficiary", ghost_beneficiary),
        ("income_inflation", income_inflation),
        ("duplicate_identity", duplicate_identity),
        ("deceased_claims", deceased_claims),
        ("scheme_hopping", scheme_hopping),
        ("address_clustering", address_clustering),
    ]:
        if name not in _PATTERNS:
            register(name, mod.detect)


_booted = False


def boot_patterns() -> None:
    """Ensure all built-in patterns are registered (idempotent)."""
    global _booted
    if _booted:
        return
    _auto_register()
    _booted = True


async def run_all(
    app_id: str,
    declared: dict,
    connector_results: list,
    all_apps_store: dict[str, dict],
) -> list[AnomalyFinding]:
    """Run every registered pattern in parallel and return aggregated findings."""
    boot_patterns()

    tasks = [
        fn(app_id, declared, connector_results, all_apps_store)
        for fn in _PATTERNS.values()
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_findings: list[AnomalyFinding] = []
    seen_types: set[str] = set()

    for pattern_name, result in zip(_PATTERNS.keys(), results):
        if isinstance(result, BaseException):
            log.warning("Pattern %s failed: %s", pattern_name, result)
            continue
        for finding in result:
            # Deduplicate by anomaly_type
            if finding.anomaly_type not in seen_types:
                seen_types.add(finding.anomaly_type)
                all_findings.append(finding)

    return all_findings
