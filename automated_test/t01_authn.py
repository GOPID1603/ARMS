"""
t01_authn.py — Authentication Tests
Verifies:
  - Unauthenticated access is blocked (401)
  - Authenticated access succeeds (200)
"""
from dast_auth import auth_headers

PROTECTED_ENDPOINTS = [
    ("GET",    "/api/data",            None,                                                                                                                      ["admin","faculty","student"]),
    ("POST",   "/api/students",        {"reg":"TST991","name":"Test","dept":"CSE","spec":"AI & ML","batch":"2026","email":"t1@t.com","phone":"9876543210","cgpa":8.5,"sem":6,"credits":120,"pass":True}, ["admin"]),
    ("POST",   "/api/notifications",   {"title":"T","msg":"T","date":"Today","priority":"info"},                                                                  ["admin"]),
    ("POST",   "/api/od",              {"date":"2026-03-25","course":"CS601","reason":"Test","student_reg":"202611001"},                                          ["student","admin"]),
    ("POST",   "/api/chatbot",         {"user_id":"202611001","role":"student","name":"T","message":"Hi"},                                                       ["admin","faculty","student"]),
    ("POST",   "/api/courses",         {"code":"TST91","name":"Test","credits":3,"dept":"CSE","sem":6,"faculty":"DG11001","schedule":"Mon 9"},                    ["admin"]),
    ("POST",   "/api/enroll",          {"student_reg":"202611001","course_code":"CS601"},                                                                        ["student","admin"]),
    ("POST",   "/api/attendance",      {"records":[{"date":"2026-01-01","course":"CS601","status":"Present","student_reg":"202611001"}]},                       ["faculty","admin"]),
]

BAD_TOKENS = [
    ("no-token",    None),
    ("empty-bearer",{"Authorization": "Bearer "}),
    ("invalid-jwt", {"Authorization": "Bearer bad.token.here"}),
]

def run(http, record, cfg, base_url):
    for method, path, body, allowed_roles in PROTECTED_ENDPOINTS:
        # ── Part A: unauthenticated → must get 401 ───────────────
        for tok_name, tok_headers in BAD_TOKENS:
            status, ms, resp = http(method, path, body=body, headers=tok_headers or {})
            finding = status != 401
            severity = "CRITICAL" if finding else "INFO"
            note = f"Auth bypass blocked correctly (401) with token={tok_name}" if not finding else \
                   f"Auth NOT enforced — got {status} with token={tok_name}"
            record(path, method, f"unauth/{tok_name}", status, 401, "AuthN-Bypass", note, ms,
                   finding=finding, severity=severity)
            if finding:
                break

        # ── Part B: authenticated → must succeed (200) ──────────
        role = allowed_roles[0]
        headers = auth_headers(http, role)
        status, ms, resp = http(method, path, body=body, headers=headers)
        finding = status not in (200, 201)
        severity = "HIGH" if finding else "INFO"
        note = f"Authenticated {role} access succeeded ({status})" if not finding else \
               f"Authenticated {role} got unexpected status {status}"
        record(path, method, f"authenticated/{role}", status, 200, "AuthN-Bypass", note, ms,
               finding=finding, severity=severity)
