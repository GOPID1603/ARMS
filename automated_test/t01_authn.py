"""
t01_authn.py — Authentication Bypass Tests
Test every protected endpoint with: no token, malformed token, expired-looking token.
Expected: 401 or 403. 200 = FINDING (no auth enforced).
"""

PROTECTED_ENDPOINTS = [
    ("GET",  "/api/data"),
    ("POST", "/api/students"),
    ("DELETE", "/api/students/202611001"),
    ("POST", "/api/notifications"),
    ("POST", "/api/disciplinary"),
    ("POST", "/api/od"),
    ("PUT",  "/api/od/1"),
    ("POST", "/api/courses"),
    ("POST", "/api/enroll"),
    ("POST", "/api/enroll/approve"),
    ("POST", "/api/attendance"),
    ("POST", "/api/chatbot"),
    ("POST", "/api/chatbot/block"),
    ("POST", "/api/seed"),
]

SAMPLE_BODIES = {
    "POST /api/students":        {"reg":"TST999","name":"Test","dept":"CSE","spec":"","batch":"2026","email":"t@t.com","phone":"9999999999","cgpa":7.0,"sem":1,"credits":0,"pass":True},
    "POST /api/notifications":   {"title":"T","msg":"T","date":"Today","priority":"info"},
    "POST /api/disciplinary":    {"student":"202611001","name":"Test","severity":"Minor","reason":"Test","date":"2026-01-01","faculty":"DG11001","notes":""},
    "POST /api/od":              {"date":"2026-01-01","course":"CS601","reason":"Test","student_reg":"202611001"},
    "PUT  /api/od/1":            {"role":"faculty","status":"Approved"},
    "POST /api/courses":         {"code":"TST01","name":"Test","credits":1,"dept":"CSE","sem":1,"faculty":"DG11001","schedule":"Mon 9"},
    "POST /api/enroll":          {"student_reg":"202611001","course_code":"CS601"},
    "POST /api/enroll/approve":  {"student_reg":"202611001","course_code":"CS601","action":"approve"},
    "POST /api/attendance":      {"records":[{"date":"2026-01-01","course":"CS601","status":"Present","student_reg":"202611001"}]},
    "POST /api/chatbot":         {"user_id":"202611001","role":"student","name":"Test","message":"Hello"},
    "POST /api/chatbot/block":   {"user_id":"202611001","role":"student","action":"block"},
    "POST /api/seed":            {},
}

BAD_TOKENS = [
    ("none",        None),
    ("empty",       {"Authorization": ""}),
    ("malformed",   {"Authorization": "Bearer INVALID.TOKEN.HERE"}),
    ("expired",     {"Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0IiwiZXhwIjoxfQ.badSig"}),
    ("sql_inject",  {"Authorization": "Bearer ' OR '1'='1"}),
]

def run(http, record, cfg, base_url):
    for method, path in PROTECTED_ENDPOINTS:
        body_key = f"{method} {path}"
        body = SAMPLE_BODIES.get(body_key) or SAMPLE_BODIES.get(path)

        for tok_name, tok_headers in BAD_TOKENS:
            status, ms, resp = http(method, path, body=body, headers=tok_headers)

            # Since this API has NO JWT enforcement (no auth middleware),
            # ANY 2xx is a finding — document it
            finding = (status < 400)  # 2xx or 3xx = auth bypass
            severity = "CRITICAL" if finding and method in ("DELETE","PUT","POST") else \
                       "HIGH"     if finding else "INFO"

            note = f"No auth enforced — {status} returned with token={tok_name}" if finding else \
                   f"Correctly rejected with {status} (token={tok_name})"

            record(path, method, f"no-auth/{tok_name}", status, 401, "AuthN-Bypass", note, ms,
                   finding=finding, severity=severity)

            if finding:
                break  # One bypass proof per endpoint is enough; don't repeat same finding
