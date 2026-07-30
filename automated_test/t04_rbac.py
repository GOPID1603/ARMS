"""
t04_rbac.py — RBAC Matrix Test
Full role × endpoint matrix with REAL tokens.
Verifies each role gets 200 on allowed endpoints and 403 on forbidden ones.
"""
from dast_auth import auth_headers

# (method, path, sample_body, roles_allowed_200, roles_forbidden_403)
MATRIX = [
    ("GET",    "/api/data",            None,
     ["admin","faculty","student"], []),
    ("POST",   "/api/students",        {"reg":"RBAC91","name":"RBAC","dept":"CSE","spec":"AI & ML","batch":"2026","email":"r1@r.com","phone":"9876543210","cgpa":8.5,"sem":6,"credits":120,"pass":True},
     ["admin"], ["faculty","student"]),
    ("POST",   "/api/notifications",   {"title":"T","msg":"T","date":"Today","priority":"info"},
     ["admin"], ["faculty","student"]),
    ("POST",   "/api/disciplinary",    {"student":"202611001","name":"T","severity":"Minor","reason":"T","date":"2026-01-01","faculty":"DG11001","notes":""},
     ["admin","faculty"], ["student"]),
    ("POST",   "/api/od",              {"date":"2026-03-25","course":"CS601","reason":"T","student_reg":"202611001"},
     ["admin","student"], ["faculty"]),
    ("PUT",    "/api/od/1",            {"role":"faculty","status":"Approved"},
     ["admin","faculty"], ["student"]),
    ("POST",   "/api/courses",         {"code":"RBAC92","name":"Test","credits":3,"dept":"CSE","sem":6,"faculty":"DG11001","schedule":"Mon 9"},
     ["admin"], ["faculty","student"]),
    ("POST",   "/api/enroll",          {"student_reg":"202611001","course_code":"CS601"},
     ["admin","student"], ["faculty"]),
    ("POST",   "/api/enroll/approve",  {"student_reg":"202611001","course_code":"CS601","action":"approve"},
     ["admin","faculty"], ["student"]),
    ("POST",   "/api/attendance",      {"records":[{"date":"2026-01-01","course":"CS601","status":"Present","student_reg":"202611001"}]},
     ["admin","faculty"], ["student"]),
    ("POST",   "/api/chatbot",         {"user_id":"202611001","role":"student","name":"T","message":"Hi"},
     ["admin","faculty","student"], []),
    ("POST",   "/api/chatbot/block",   {"user_id":"202611001","role":"student","action":"block"},
     ["admin"], ["faculty","student"]),
]

def run(http, record, cfg, base_url):
    for method, path, body, allowed, forbidden in MATRIX:
        # Test allowed roles → expected 200/201
        for role in allowed:
            hdrs = auth_headers(http, role)
            status, ms, resp = http(method, path, body=body, headers=hdrs)
            finding = status not in (200, 201)
            note = f"Role={role} correctly allowed on {method} {path} (got {status})" if not finding else \
                   f"RBAC: role={role} should be allowed but got {status}"
            record(path, method, f"rbac/allowed/{role}", status, 200, "RBAC-Matrix", note, ms,
                   finding=finding, severity="HIGH" if finding else "INFO")

        # Test forbidden roles → expected 403
        for role in forbidden:
            hdrs = auth_headers(http, role)
            status, ms, resp = http(method, path, body=body, headers=hdrs)
            finding = status != 403
            note = f"Role={role} correctly blocked (403) on {method} {path}" if not finding else \
                   f"RBAC violation: role={role} got {status} (expected 403)"
            record(path, method, f"rbac/forbidden/{role}", status, 403, "RBAC-Matrix", note, ms,
                   finding=finding, severity="MEDIUM" if finding else "INFO")
