"""
t02_authz.py — Authorization / Privilege Escalation Tests
Call admin-only / faculty-only endpoints without admin credentials.
The API uses client-side role enforcement only (no server-side JWT).
Any 2xx from a lower-role caller = FINDING.
"""

# Endpoints that should be admin-only based on business logic
ADMIN_ONLY = [
    ("POST",   "/api/students",       {"reg":"TST888","name":"Hack","dept":"CSE","spec":"","batch":"2026","email":"h@h.com","phone":"9999999998","cgpa":7.0,"sem":1,"credits":0,"pass":True}),
    ("DELETE", "/api/students/202611001", None),
    ("POST",   "/api/notifications",  {"title":"Hacked","msg":"Hacked","date":"Today","priority":"danger"}),
    ("POST",   "/api/courses",        {"code":"HCK01","name":"Hack Course","credits":1,"dept":"CSE","sem":1,"faculty":"DG11001","schedule":"Mon 9"}),
    ("POST",   "/api/chatbot/block",  {"user_id":"202611002","role":"student","action":"block"}),
    ("POST",   "/api/seed",           {}),
]

# Endpoints that should be faculty-only
FACULTY_ONLY = [
    ("POST",   "/api/disciplinary",   {"student":"202611001","name":"Test","severity":"Minor","reason":"Test","date":"2026-01-01","faculty":"DG11001","notes":""}),
    ("PUT",    "/api/od/1",           {"role":"faculty","status":"Approved"}),
    ("POST",   "/api/attendance",     {"records":[{"date":"2026-01-01","course":"CS601","status":"Present","student_reg":"202611001"}]}),
    ("POST",   "/api/enroll/approve", {"student_reg":"202611001","course_code":"CS601","action":"approve"}),
]

def run(http, record, cfg, base_url):
    # Test admin-only endpoints as student (lower privilege)
    for method, path, body in ADMIN_ONLY:
        status, ms, resp = http(method, path, body=body)
        finding = status < 400
        severity = "CRITICAL" if finding and method in ("DELETE","POST") else "HIGH" if finding else "INFO"
        note = f"Privilege escalation: student accessed admin endpoint — got {status}" if finding else \
               f"Correctly blocked with {status}"
        record(path, method, "student(→admin)", status, 403, "AuthZ-Privesc", note, ms,
               finding=finding, severity=severity)

    # Test faculty-only endpoints as student
    for method, path, body in FACULTY_ONLY:
        status, ms, resp = http(method, path, body=body)
        finding = status < 400
        severity = "HIGH" if finding else "INFO"
        note = f"Privilege escalation: student accessed faculty endpoint — got {status}" if finding else \
               f"Correctly blocked with {status}"
        record(path, method, "student(→faculty)", status, 403, "AuthZ-Privesc", note, ms,
               finding=finding, severity=severity)
