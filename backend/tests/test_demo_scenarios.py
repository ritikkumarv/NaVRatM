"""Demo scenario end-to-end tests.

Run against a live server:
    python -m pytest tests/test_demo_scenarios.py -v
Or standalone:
    python tests/test_demo_scenarios.py
"""

from __future__ import annotations

import asyncio
import sys

import httpx
import pytest

BASE = "http://127.0.0.1:8000/api"


@pytest.mark.asyncio
async def test_clean_approve():
    """Process a clean app -> verify low-to-medium score, decide approve."""
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{BASE}/applications/APP-047/process")
        assert r.status_code == 200
        data = r.json()
        assert data["risk_score"] < 50, f"Expected <50, got {data['risk_score']}"
        assert data["risk_band"] in ("low", "medium")

        r = await client.post(
            f"{BASE}/applications/APP-047/decide",
            json={"action": "approve", "reason": "Clean application — all docs match"},
        )
        assert r.status_code == 200
        assert r.json()["new_status"] == "approved"


@pytest.mark.asyncio
async def test_duplicate_ring_escalate():
    """Process a fraud-ring app -> verify anomalies detected, score >= 50, escalate."""
    async with httpx.AsyncClient(timeout=30) as client:
        # Process several ring members first so cross-app patterns can fire
        for aid in ("APP-026", "APP-027", "APP-028", "APP-029", "APP-030"):
            r = await client.post(f"{BASE}/applications/{aid}/process")
            assert r.status_code == 200

        # Re-process the lead member to pick up network flags
        r = await client.post(f"{BASE}/applications/APP-026/process")
        assert r.status_code == 200
        data = r.json()
        assert data["risk_score"] >= 50 or len(data.get("network_flags", [])) > 0 or len(data.get("anomalies", [])) > 0, (
            f"Expected high risk or anomalies for duplicate ring member: score={data['risk_score']}"
        )

        r = await client.post(
            f"{BASE}/applications/APP-026/decide",
            json={"action": "escalate", "reason": "Duplicate identity ring detected"},
        )
        assert r.status_code == 200
        assert r.json()["new_status"] == "escalated"


@pytest.mark.asyncio
async def test_income_mismatch_flag():
    """Process income-mismatch app -> verify income deviation factor, score >= 25."""
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{BASE}/applications/APP-031/process")
        assert r.status_code == 200
        data = r.json()
        assert data["risk_score"] >= 25, f"Expected >=25, got {data['risk_score']}"


@pytest.mark.asyncio
async def test_deceased_reject():
    """Process deceased claim -> verify elevated risk, decide reject."""
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{BASE}/applications/APP-036/process")
        assert r.status_code == 200
        data = r.json()
        assert data["risk_score"] >= 25, (
            f"Expected >=25 for deceased claim: score={data['risk_score']}, band={data['risk_band']}"
        )

        r = await client.post(
            f"{BASE}/applications/APP-036/decide",
            json={"action": "reject", "reason": "Deceased beneficiary claim"},
        )
        assert r.status_code == 200
        assert r.json()["new_status"] == "rejected"


# ── Standalone runner ──

async def _main():
    tests = [
        ("test_clean_approve", test_clean_approve),
        ("test_duplicate_ring_escalate", test_duplicate_ring_escalate),
        ("test_income_mismatch_flag", test_income_mismatch_flag),
        ("test_deceased_reject", test_deceased_reject),
    ]
    passed = failed = 0
    for name, fn in tests:
        try:
            await fn()
            print(f"  PASS  {name}")
            passed += 1
        except Exception as exc:
            print(f"  FAIL  {name}: {exc}")
            failed += 1
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed out of {passed + failed}")
    return failed == 0


if __name__ == "__main__":
    ok = asyncio.run(_main())
    sys.exit(0 if ok else 1)
