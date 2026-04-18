"""Sarvam AI connection diagnostic — tests multiple approaches.

Run: python test_sarvam_connection.py
"""

import asyncio
import os
import ssl
import sys
import socket
import urllib.request
import json

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

API_KEY = os.getenv("SARVAM_API_KEY", "")
BASE = "https://api.sarvam.ai"

print("=" * 60)
print("SARVAM AI CONNECTION DIAGNOSTIC")
print("=" * 60)


# ── 0. Env check ──
def check_env():
    print("\n[0] ENV CHECK")
    if not API_KEY:
        print("  ✗ SARVAM_API_KEY is EMPTY — nothing will work")
        return False
    print(f"  ✓ SARVAM_API_KEY loaded (starts with {API_KEY[:8]}...)")
    return True


# ── 1. DNS resolution ──
def check_dns():
    print("\n[1] DNS RESOLUTION")
    try:
        ip = socket.getaddrinfo("api.sarvam.ai", 443, socket.AF_INET)
        print(f"  ✓ api.sarvam.ai resolves to {ip[0][4][0]}")
        return True
    except socket.gaierror as e:
        print(f"  ✗ DNS failed: {e}")
        return False


# ── 2. TCP connectivity ──
def check_tcp():
    print("\n[2] TCP CONNECTIVITY (port 443)")
    try:
        sock = socket.create_connection(("api.sarvam.ai", 443), timeout=10)
        sock.close()
        print("  ✓ TCP connection successful")
        return True
    except (socket.timeout, OSError) as e:
        print(f"  ✗ TCP connection failed: {e}")
        return False


# ── 3. SSL/TLS handshake ──
def check_ssl():
    print("\n[3] SSL/TLS HANDSHAKE")
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection(("api.sarvam.ai", 443), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname="api.sarvam.ai") as ssock:
                cert = ssock.getpeercert()
                print(f"  ✓ TLS version: {ssock.version()}")
                print(f"  ✓ Cipher: {ssock.cipher()[0]}")
                cn = dict(x[0] for x in cert["subject"])["commonName"]
                print(f"  ✓ Cert CN: {cn}")
                return True
    except ssl.SSLError as e:
        print(f"  ✗ SSL error: {e}")
        print("  → Try setting SARVAM_SSL_VERIFY=false in .env")
        return False
    except Exception as e:
        print(f"  ✗ Unexpected: {e}")
        return False


# ── 4. urllib (stdlib — no third-party deps) ──
def check_urllib():
    print("\n[4] STDLIB urllib (translate endpoint — simple POST)")
    payload = json.dumps({
        "input": "Hello",
        "source_language_code": "en-IN",
        "target_language_code": "hi-IN",
        "model": "mayura:v1",
    }).encode()
    req = urllib.request.Request(
        f"{BASE}/translate",
        data=payload,
        headers={
            "api-subscription-key": API_KEY,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read())
            print(f"  ✓ Status: {resp.status}")
            print(f"  ✓ Response: {body}")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        print(f"  ✗ HTTP {e.code}: {body}")
        return False
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


# ── 5. urllib with SSL disabled ──
def check_urllib_no_ssl():
    print("\n[5] STDLIB urllib (SSL verification DISABLED)")
    payload = json.dumps({
        "input": "Hello",
        "source_language_code": "en-IN",
        "target_language_code": "hi-IN",
        "model": "mayura:v1",
    }).encode()
    req = urllib.request.Request(
        f"{BASE}/translate",
        data=payload,
        headers={
            "api-subscription-key": API_KEY,
            "Content-Type": "application/json",
        },
    )
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            body = json.loads(resp.read())
            print(f"  ✓ Status: {resp.status}")
            print(f"  ✓ Response: {body}")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        print(f"  ✗ HTTP {e.code}: {body}")
        return False
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False


# ── 6. httpx sync (what our app uses, but sync) ──
def check_httpx_sync():
    print("\n[6] HTTPX SYNC (mirrors app usage)")
    try:
        import httpx
    except ImportError:
        print("  ✗ httpx not installed — skip")
        return None
    try:
        with httpx.Client(timeout=15, verify=True) as c:
            resp = c.post(
                f"{BASE}/translate",
                headers={"api-subscription-key": API_KEY},
                json={
                    "input": "Hello",
                    "source_language_code": "en-IN",
                    "target_language_code": "hi-IN",
                    "model": "mayura:v1",
                },
            )
            print(f"  ✓ Status: {resp.status_code}")
            print(f"  ✓ Body: {resp.json()}")
            return True
    except Exception as e:
        print(f"  ✗ httpx (verify=True) failed: {type(e).__name__}: {e}")

    # Retry without SSL
    print("  → Retrying with verify=False ...")
    try:
        with httpx.Client(timeout=15, verify=False) as c:
            resp = c.post(
                f"{BASE}/translate",
                headers={"api-subscription-key": API_KEY},
                json={
                    "input": "Hello",
                    "source_language_code": "en-IN",
                    "target_language_code": "hi-IN",
                    "model": "mayura:v1",
                },
            )
            print(f"  ✓ Status (no-verify): {resp.status_code}")
            print(f"  ✓ Body: {resp.json()}")
            print("  ⚠ Works WITHOUT SSL — your proxy/corp cert breaks verification")
            print("    → Set SARVAM_SSL_VERIFY=false in .env")
            return "ssl_issue"
    except Exception as e2:
        print(f"  ✗ httpx (verify=False) also failed: {type(e2).__name__}: {e2}")
        return False


# ── 7. httpx async (exactly how app calls) ──
async def check_httpx_async():
    print("\n[7] HTTPX ASYNC (exact app pattern)")
    try:
        import httpx
    except ImportError:
        print("  ✗ httpx not installed — skip")
        return None
    try:
        async with httpx.AsyncClient(timeout=15, verify=True) as c:
            resp = await c.post(
                f"{BASE}/translate",
                headers={"api-subscription-key": API_KEY},
                json={
                    "input": "Test",
                    "source_language_code": "en-IN",
                    "target_language_code": "hi-IN",
                    "model": "mayura:v1",
                },
            )
            print(f"  ✓ Status: {resp.status_code}")
            print(f"  ✓ Body: {resp.json()}")
            return True
    except Exception as e:
        print(f"  ✗ Async (verify=True) failed: {type(e).__name__}: {e}")

    print("  → Retrying async with verify=False ...")
    try:
        async with httpx.AsyncClient(timeout=15, verify=False) as c:
            resp = await c.post(
                f"{BASE}/translate",
                headers={"api-subscription-key": API_KEY},
                json={
                    "input": "Test",
                    "source_language_code": "en-IN",
                    "target_language_code": "hi-IN",
                    "model": "mayura:v1",
                },
            )
            print(f"  ✓ Status (no-verify): {resp.status_code}")
            print(f"  ✓ Body: {resp.json()}")
            return "ssl_issue"
    except Exception as e2:
        print(f"  ✗ Async (verify=False) also failed: {type(e2).__name__}: {e2}")
        return False


# ── 8. sarvamai SDK ──
def check_sdk():
    print("\n[8] SARVAMAI SDK (official package)")
    try:
        from sarvamai import SarvamAI
    except ImportError:
        print("  ✗ sarvamai not installed — pip install sarvamai")
        return None
    try:
        client = SarvamAI(api_subscription_key=API_KEY)
        resp = client.text.translate(
            input="Hello world",
            source_language_code="en-IN",
            target_language_code="hi-IN",
        )
        print(f"  ✓ SDK response: {resp}")
        return True
    except Exception as e:
        print(f"  ✗ SDK failed: {type(e).__name__}: {e}")
        return False


# ── Run all ──
def main():
    ok = check_env()
    if not ok:
        sys.exit(1)

    results = {}
    results["dns"] = check_dns()
    results["tcp"] = check_tcp()
    results["ssl"] = check_ssl()
    results["urllib"] = check_urllib()
    if not results["urllib"]:
        results["urllib_nossl"] = check_urllib_no_ssl()
    results["httpx_sync"] = check_httpx_sync()
    results["httpx_async"] = asyncio.run(check_httpx_async())
    results["sdk"] = check_sdk()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for k, v in results.items():
        icon = "✓" if v is True else ("⚠" if v == "ssl_issue" else ("⊘" if v is None else "✗"))
        print(f"  {icon} {k}")

    if all(v is True or v is None for v in results.values()):
        print("\n→ All tests passed. Issue is NOT on your end — Sarvam API is reachable.")
    elif any(v == "ssl_issue" for v in results.values()):
        print("\n→ SSL/corporate proxy issue. Add SARVAM_SSL_VERIFY=false to .env")
    elif not results.get("dns"):
        print("\n→ DNS failure — check internet / VPN.")
    elif not results.get("tcp"):
        print("\n→ Firewall blocking port 443 to api.sarvam.ai.")
    elif not results.get("ssl"):
        print("\n→ SSL cert chain broken — corporate proxy likely intercepting.")
    else:
        print("\n→ Network is fine but API returns errors — check API key validity.")


if __name__ == "__main__":
    main()
