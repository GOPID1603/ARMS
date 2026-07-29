# -*- coding: utf-8 -*-
"""
ARMS Portal — DAST Runner
Reads configuration from input.json, runs all security test categories,
and writes results to report.json.
"""
import json, time, datetime, sys, os, re, subprocess, socket
from pathlib import Path

BASE = Path(__file__).parent

# ─── Load config ──────────────────────────────────────────────────
cfg = json.loads((BASE / "input.json").read_text())
BASE_URL = cfg["baseUrl"].rstrip("/")

# Parse host/port for availability check
import urllib.parse as up
parsed = up.urlparse(BASE_URL)
HOST = parsed.hostname
PORT = parsed.port or (443 if parsed.scheme == "https" else 80)

# ─── Check server is reachable ────────────────────────────────────
def server_up():
    try:
        s = socket.create_connection((HOST, PORT), timeout=3)
        s.close()
        return True
    except Exception:
        return False

# ─── HTTP helper (uses urllib — no external deps) ─────────────────
import urllib.request, urllib.error

def http(method, path, body=None, headers=None, timeout=10):
    url = BASE_URL + path
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            status = r.status
            resp_body = r.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        status = e.code
        resp_body = e.read().decode(errors="replace")
    except Exception as ex:
        status = 0
        resp_body = str(ex)
    ms = round((time.time() - t0) * 1000)
    return status, ms, resp_body

# ─── Result store ─────────────────────────────────────────────────
results = []
SEVERITY_ORDER = {"CRITICAL":0,"HIGH":1,"MEDIUM":2,"LOW":3,"INFO":4}

def record(endpoint, method, role, status, expected, category, note, ms, finding=None, severity="INFO"):
    if finding is None:
        finding = (status != expected) or (status == 200 and expected != 200)
    results.append({
        "endpoint": endpoint, "method": method, "role": role,
        "status": status, "expected_status": expected,
        "finding": finding, "severity": severity,
        "response_time_ms": ms, "test_category": category,
        "note": note, "timestamp": datetime.datetime.utcnow().isoformat()+"Z"
    })
    sym = "[OK]" if finding is False else "[!!]"
    print(f"  {sym} [{category}] {method:6} {endpoint:35} | role={role:10} | {status} (exp {expected}) | {ms}ms | {note}")

# ─── Import individual test modules ──────────────────────────────
sys.path.insert(0, str(BASE))
from t01_authn      import run as run_authn
from t02_authz      import run as run_authz
from t03_idor       import run as run_idor
from t04_rbac       import run as run_rbac
from t05_token_tamper import run as run_tamper
from t06_injection  import run as run_injection
from t07_ratelimit  import run as run_ratelimit
from t08_hardcoded  import run as run_hardcoded

# ─── MAIN ────────────────────────────────────────────────────────
def main():
    print("\n" + "="*65)
    print("  ARMS Portal — DAST Security Test Suite")
    print("="*65)
    sys.stdout.reconfigure(encoding='utf-8', errors='replace') if hasattr(sys.stdout,'reconfigure') else None
    print(f"  Target : {BASE_URL}")
    print(f"  Time   : {datetime.datetime.utcnow().isoformat()}Z")
    print("="*65 + "\n")

    if not server_up():
        print(f"[WARN] Server at {BASE_URL} is NOT reachable.")
        print("   Please start the Flask backend (python backend/app.py)")
        print("   and re-run this script.\n")
        print("   Still running static codebase scan (t08) which needs no live server")
        print("\n[8] Hardcoded Credentials / Secrets Scan")
        run_hardcoded(http, record, cfg, BASE_URL)
    else:
        print(f"[OK] Server reachable at {BASE_URL}\n")
        print("[1] Authentication Bypass")
        run_authn(http, record, cfg, BASE_URL)
        time.sleep(0.5)

        print("\n[2] Authorization / Privilege Escalation")
        run_authz(http, record, cfg, BASE_URL)
        time.sleep(0.5)

        print("\n[3] IDOR — Insecure Direct Object Reference")
        run_idor(http, record, cfg, BASE_URL)
        time.sleep(0.5)

        print("\n[4] RBAC Matrix")
        run_rbac(http, record, cfg, BASE_URL)
        time.sleep(0.5)

        print("\n[5] Token Tampering")
        run_tamper(http, record, cfg, BASE_URL)
        time.sleep(0.5)

        print("\n[6] Injection Probes (SQLi / NoSQLi detection)")
        run_injection(http, record, cfg, BASE_URL)
        time.sleep(0.5)

        print("\n[7] Rate Limiting Check")
        run_ratelimit(http, record, cfg, BASE_URL)
        time.sleep(0.5)

        print("\n[8] Hardcoded Credentials / Secrets Scan")
        run_hardcoded(http, record, cfg, BASE_URL)

    # ─── Write report ────────────────────────────────────────────
    report_path = BASE / "report.json"
    report_path.write_text(json.dumps(results, indent=2))

    # ─── Print summary ───────────────────────────────────────────
    findings = [r for r in results if r["finding"]]
    total    = len(results)
    print("\n" + "="*65)
    print("  SUMMARY")
    print("="*65)
    print(f"  Endpoints tested : {len({r['endpoint'] for r in results})}")
    print(f"  Total tests run  : {total}")
    print(f"  Findings         : {len(findings)}")
    print()
    for sev in ["CRITICAL","HIGH","MEDIUM","LOW","INFO"]:
        grp = [r for r in findings if r["severity"] == sev]
        if grp:
            print(f"  {sev:8}: {len(grp)}")
            for r in grp:
                note_short = r['note'][:80]
                print(f"    [!!] [{r['test_category']}] {r['method']} {r['endpoint']} ({note_short})")
    print()
    print(f"  Full report written to: {report_path}")
    print("="*65 + "\n")

if __name__ == "__main__":
    main()
