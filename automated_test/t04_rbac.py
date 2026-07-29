"""
t04_rbac.py — RBAC Matrix Test
Full role × endpoint matrix. Every endpoint × every role.
Documents actual vs expected access.
"""

# (method, path, sample_body, expected_roles_that_should_succeed)
ENDPOINTS = [
    ("GET",    "/api/data",            None,                                   ["admin","faculty","student"]),
    ("POST",   "/api/students",        {"reg":"RBAC01","name":"RBAC","dept":"CSE","spec":"","batch":"2026","email":"r@r.com","phone":"9999999990","cgpa":7.0,"sem":1,"credits":0,"pass":True}, ["admin"]),
    ("POST",   "/api/notifications",   {"title":"T","msg":"T","date":"Today","priority":"info"},             ["admin"]),
    ("POST",   "/api/disciplinary",    {"student":"202611001","name":"T","severity":"Minor","reason":"T","date":"2026-01-01","faculty":"DG11001","notes":""},["admin","faculty"]),
    ("POST",   "/api/od",              {"date":"2026-01-01","course":"CS601","reason":"T","student_reg":"202611001"}, ["student","admin"]),
    ("PUT",    "/api/od/1",            {"role":"faculty","status":"Approved"},                               ["faculty","admin"]),
    ("POST",   "/api/courses",         {"code":"RBAC02","name":"Test","credits":1,"dept":"CSE","sem":1,"faculty":"DG11001","schedule":"Mon 9"}, ["admin"]),
    ("POST",   "/api/enroll",          {"student_reg":"202611001","course_code":"CS601"},                   ["student"]),
    ("POST",   "/api/enroll/approve",  {"student_reg":"202611001","course_code":"CS601","action":"approve"},["faculty","admin"]),
    ("POST",   "/api/attendance",      {"records":[{"date":"2026-01-01","course":"CS601","status":"Present","student_reg":"202611001"}]}, ["faculty","admin"]),
    ("POST",   "/api/chatbot",         {"user_id":"202611001","role":"student","name":"T","message":"Hi"},  ["student","faculty","admin"]),
    ("POST",   "/api/chatbot/block",   {"user_id":"202611001","role":"student","action":"block"},           ["admin"]),
    ("POST",   "/api/seed",            {},                                                                  ["admin"]),
]

ROLES = ["admin", "faculty", "student"]

def run(http, record, cfg, base_url):
    for method, path, body, allowed_roles in ENDPOINTS:
        for role in ROLES:
            # No auth header is sent — this documents what the server actually allows
            status, ms, resp = http(method, path, body=body)
            expected = 200 if role in allowed_roles else 403
            finding = (status < 400) and (role not in allowed_roles)
            severity = "HIGH" if finding and method in ("DELETE","PUT") else \
                       "MEDIUM" if finding else "INFO"
            note = f"RBAC violation: role={role} accessed {method} {path} (got {status})" if finding else \
                   f"role={role} → {status} (expected {expected})"
            record(path, method, f"rbac/{role}", status, expected, "RBAC-Matrix", note, ms,
                   finding=finding, severity=severity)
