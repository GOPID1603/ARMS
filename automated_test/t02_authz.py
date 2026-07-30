"""
t02_authz.py — Authorization / Privilege Escalation Tests
Verifies: lower-privilege role cannot access higher-privilege endpoints (403).
"""
from dast_auth import auth_headers

# (method, path, body, role_that_should_be_blocked, expected_status_when_blocked)
CROSS_ROLE_TESTS = [
    # Student trying admin-only endpoints
    ("POST",   "/api/students",       {"reg":"TST881","name":"Hack","dept":"CSE","spec":"","batch":"2026","email":"h1@h.com","phone":"9999999881","cgpa":7.0,"sem":1,"credits":0,"pass":True}, "student", 403),
    ("POST",   "/api/notifications",  {"title":"T","msg":"T","date":"Today","priority":"info"}, "student", 403),
    ("POST",   "/api/courses",        {"code":"HCK91","name":"Hack","credits":1,"dept":"CSE","sem":1,"faculty":"DG11001","schedule":"Mon 9"}, "student", 403),
    ("POST",   "/api/chatbot/block",  {"user_id":"202611002","role":"student","action":"block"}, "student", 403),
    ("POST",   "/api/seed",           {}, "student", 403),
    # Student trying faculty-only endpoints
    ("POST",   "/api/disciplinary",   {"student":"202611001","name":"T","severity":"Minor","reason":"T","date":"2026-01-01","faculty":"DG11001","notes":""}, "student", 403),
    ("PUT",    "/api/od/1",           {"role":"faculty","status":"Approved"}, "student", 403),
    ("POST",   "/api/attendance",     {"records":[{"date":"2026-01-01","course":"CS601","status":"Present","student_reg":"202611001"}]}, "student", 403),
    ("POST",   "/api/enroll/approve", {"student_reg":"202611001","course_code":"CS601","action":"approve"}, "student", 403),
    # Faculty trying admin-only endpoints
    ("POST",   "/api/students",       {"reg":"TST882","name":"Hack","dept":"CSE","spec":"","batch":"2026","email":"h2@h.com","phone":"9999999882","cgpa":7.0,"sem":1,"credits":0,"pass":True}, "faculty", 403),
    ("POST",   "/api/chatbot/block",  {"user_id":"202611002","role":"student","action":"block"}, "faculty", 403),
]

def run(http, record, cfg, base_url):
    for method, path, body, blocked_role, expected in CROSS_ROLE_TESTS:
        headers = auth_headers(http, blocked_role)
        status, ms, resp = http(method, path, body=body, headers=headers)
        finding = status != expected  # PASS = correctly returned 403
        severity = "CRITICAL" if finding else "INFO"
        note = f"Correctly rejected {blocked_role} → {method} {path} with {status}" if not finding else \
               f"Privilege escalation: {blocked_role} accessed {method} {path} — got {status} (expected {expected})"
        record(path, method, f"privesc/{blocked_role}", status, expected, "AuthZ-Privesc", note, ms,
               finding=finding, severity=severity)
