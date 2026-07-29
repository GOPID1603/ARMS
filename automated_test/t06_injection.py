"""
t06_injection.py — SQL / NoSQLi Injection Detection
Send classic injection payloads in path and body params.
Flag: anomalous status (500), stack traces in body, timing anomalies (>2s).
Detection only — no data extraction.
"""
import time

SQLI_PAYLOADS = [
    "' OR '1'='1",
    "'; DROP TABLE students; --",
    "1 UNION SELECT null,null,null--",
    "' AND 1=SLEEP(2)--",
    "\" OR \"1\"=\"1",
    "admin'--",
]

def run(http, record, cfg, base_url):

    # ── 1. Path-param injection on /api/students/<reg> (DELETE) ──────
    for payload in SQLI_PAYLOADS:
        import urllib.parse
        safe = urllib.parse.quote(payload, safe="")
        status, ms, resp = http("DELETE", f"/api/students/{safe}")
        error_leaked = any(kw in resp.lower() for kw in ["traceback","sqlite","error","exception","syntax"])
        timing_anomaly = ms > 2000
        finding = status == 500 or error_leaked or timing_anomaly
        severity = "HIGH" if finding else "INFO"
        note = f"Injection probe in path param: status={status}, error_leak={error_leaked}, ms={ms}" if finding else \
               f"No anomaly detected for payload: {payload[:30]}"
        record(f"/api/students/{{reg}}", "DELETE", "injection/path", status, 403,
               "Injection", note, ms, finding=finding, severity=severity)

    # ── 2. Body-param injection on /api/od ──────────────────────────
    for payload in SQLI_PAYLOADS:
        body = {"date": payload, "course": payload, "reason": payload, "student_reg": payload}
        status, ms, resp = http("POST", "/api/od", body=body)
        error_leaked = any(kw in resp.lower() for kw in ["traceback","sqlite","sql","syntax error","operational"])
        timing_anomaly = ms > 2000
        finding = status == 500 or error_leaked or timing_anomaly
        severity = "HIGH" if finding else "INFO"
        note = f"Injection probe in POST body: status={status}, error_leak={error_leaked}, ms={ms}" if finding else \
               f"No anomaly on POST /api/od with payload: {payload[:30]}"
        record("/api/od", "POST", "injection/body", status, 200,
               "Injection", note, ms, finding=finding, severity=severity)

    # ── 3. Chatbot message injection ─────────────────────────────────
    for payload in SQLI_PAYLOADS:
        body = {"user_id": payload, "role": "student", "name": "T", "message": payload}
        status, ms, resp = http("POST", "/api/chatbot", body=body)
        error_leaked = any(kw in resp.lower() for kw in ["traceback","sqlite","error","exception"])
        finding = status == 500 or error_leaked
        severity = "MEDIUM" if finding else "INFO"
        note = f"Chatbot injection: status={status}, error_leak={error_leaked}" if finding else \
               f"No anomaly on chatbot with payload: {payload[:30]}"
        record("/api/chatbot", "POST", "injection/chatbot", status, 200,
               "Injection", note, ms, finding=finding, severity=severity)

    # ── 4. Notification body injection ───────────────────────────────
    for payload in SQLI_PAYLOADS:
        body = {"title": payload, "msg": payload, "date": "Today", "priority": payload}
        status, ms, resp = http("POST", "/api/notifications", body=body)
        error_leaked = any(kw in resp.lower() for kw in ["traceback","sqlite","syntax"])
        finding = status == 500 or error_leaked
        severity = "HIGH" if finding else "INFO"
        note = f"Notif injection: status={status}, error_leak={error_leaked}" if finding else \
               f"No anomaly in notifications with payload: {payload[:30]}"
        record("/api/notifications", "POST", "injection/notif", status, 200,
               "Injection", note, ms, finding=finding, severity=severity)
