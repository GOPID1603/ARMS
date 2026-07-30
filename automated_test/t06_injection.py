"""
t06_injection.py — SQL / NoSQLi Injection Detection
Send classic injection payloads in path and body params with valid auth tokens.
Flag: anomalous status (500), stack traces in body, timing anomalies (>2s).
"""
import time
from dast_auth import auth_headers

SQLI_PAYLOADS = [
    "' OR '1'='1",
    "'; DROP TABLE students; --",
    "1 UNION SELECT null,null,null--",
    "' AND 1=SLEEP(2)--",
    "\" OR \"1\"=\"1",
    "admin'--",
]

def run(http, record, cfg, base_url):
    admin_hdrs = auth_headers(http, "admin")
    student_hdrs = auth_headers(http, "student")

    # ── 1. Path-param injection on /api/students/<reg> (DELETE) ──────
    for payload in SQLI_PAYLOADS:
        import urllib.parse
        safe = urllib.parse.quote(payload, safe="")
        status, ms, resp = http("DELETE", f"/api/students/{safe}", headers=admin_hdrs)
        error_leaked = any(kw in resp.lower() for kw in ["traceback", "sqlite", "syntax error", "operationalerror"])
        timing_anomaly = ms > 2000
        finding = status == 500 or error_leaked or timing_anomaly
        severity = "HIGH" if finding else "INFO"
        note = f"Injection probe in path param: status={status}, error_leak={error_leaked}, ms={ms}" if finding else \
               f"No anomaly detected for payload: {payload[:30]}"
        record(f"/api/students/{{reg}}", "DELETE", "injection/path", status, 200 if status==200 else 400,
               "Injection", note, ms, finding=finding, severity=severity)

    # ── 2. Body-param injection on /api/od ──────────────────────────
    for payload in SQLI_PAYLOADS:
        body = {"date": payload, "course": payload, "reason": payload, "student_reg": payload}
        status, ms, resp = http("POST", "/api/od", body=body, headers=student_hdrs)
        error_leaked = any(kw in resp.lower() for kw in ["traceback", "sqlite", "syntax error", "operationalerror"])
        timing_anomaly = ms > 2000
        finding = status == 500 or error_leaked or timing_anomaly
        severity = "HIGH" if finding else "INFO"
        note = f"Injection probe in POST body: status={status}, error_leak={error_leaked}, ms={ms}" if finding else \
               f"No anomaly on POST /api/od with payload: {payload[:30]}"
        record("/api/od", "POST", "injection/body", status, 200 if status==200 else 400,
               "Injection", note, ms, finding=finding, severity=severity)

    # ── 3. Chatbot message injection ─────────────────────────────────
    for payload in SQLI_PAYLOADS:
        body = {"user_id": "202611001", "role": "student", "name": "T", "message": payload}
        status, ms, resp = http("POST", "/api/chatbot", body=body, headers=student_hdrs)
        error_leaked = any(kw in resp.lower() for kw in ["traceback", "sqlite", "syntax error", "operationalerror"])
        finding = status == 500 or error_leaked
        severity = "MEDIUM" if finding else "INFO"
        note = f"Chatbot injection: status={status}, error_leak={error_leaked}" if finding else \
               f"No anomaly on chatbot with payload: {payload[:30]}"
        record("/api/chatbot", "POST", "injection/chatbot", status, 200 if status==200 else 400,
               "Injection", note, ms, finding=finding, severity=severity)

    # ── 4. Notification body injection ───────────────────────────────
    for payload in SQLI_PAYLOADS:
        body = {"title": payload, "msg": payload, "date": "Today", "priority": "info"}
        status, ms, resp = http("POST", "/api/notifications", body=body, headers=admin_hdrs)
        error_leaked = any(kw in resp.lower() for kw in ["traceback", "sqlite", "syntax error", "operationalerror"])
        finding = status == 500 or error_leaked
        severity = "HIGH" if finding else "INFO"
        note = f"Notif injection: status={status}, error_leak={error_leaked}" if finding else \
               f"No anomaly in notifications with payload: {payload[:30]}"
        record("/api/notifications", "POST", "injection/notif", status, 200 if status==200 else 400,
               "Injection", note, ms, finding=finding, severity=severity)
