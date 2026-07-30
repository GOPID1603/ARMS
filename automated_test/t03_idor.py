"""
t03_idor.py — IDOR Tests
Verifies unauthenticated access is blocked and authenticated access is scoped.
"""
from dast_auth import auth_headers

def run(http, record, cfg, base_url):
    # Test 1: /api/data requires auth → 401 without token
    status, ms, resp = http("GET", "/api/data")
    finding = status != 401
    note = f"IDOR blocked: /api/data requires auth, got {status}" if not finding else \
           f"IDOR: /api/data accessible without auth (got {status})"
    record("/api/data", "GET", "unauthenticated", status, 401, "IDOR", note, ms,
           finding=finding, severity="CRITICAL" if finding else "INFO")

    # Test 2: /api/data with valid auth → should succeed
    hdrs = auth_headers(http, "admin")
    status, ms, resp = http("GET", "/api/data", headers=hdrs)
    finding = status not in (200, 201)
    note = f"Authenticated /api/data returns data (status={status})" if not finding else \
           f"Unexpected status on authenticated /api/data: {status}"
    record("/api/data", "GET", "admin", status, 200, "IDOR", note, ms,
           finding=finding, severity="HIGH" if finding else "INFO")

    # Test 3: DELETE without auth → 401
    for fake_reg in ["999999999", "../../etc/passwd"]:
        import urllib.parse
        safe = urllib.parse.quote(fake_reg, safe="")
        status, ms, resp = http("DELETE", f"/api/students/{safe}")
        finding = status in (200, 201)
        note = f"IDOR blocked: DELETE without auth returned {status}" if not finding else \
               f"IDOR: DELETE /api/students/{fake_reg} without auth returned {status}"
        record(f"/api/students/{{reg}}", "DELETE", "unauthenticated", status, 401, "IDOR", note, ms,
               finding=finding, severity="CRITICAL" if finding else "INFO")

    # Test 4: OD update without auth → 401
    for od_id in [1, 9999]:
        status, ms, resp = http("PUT", f"/api/od/{od_id}", body={"role":"admin","status":"Approved"})
        finding = status not in (401, 403)
        note = f"IDOR blocked: PUT /api/od/{od_id} without auth returned {status}" if not finding else \
               f"IDOR: PUT /api/od/{od_id} without auth got {status}"
        record(f"/api/od/{{id}}", "PUT", "unauthenticated", status, 401, "IDOR", note, ms,
               finding=finding, severity="HIGH" if finding else "INFO")

    # Test 5: Enroll without auth → 401
    status, ms, resp = http("POST", "/api/enroll",
                            body={"student_reg": "202611002", "course_code": "CS601"})
    finding = status not in (401, 403)
    note = f"IDOR blocked: enroll without auth returned {status}" if not finding else \
           f"IDOR: /api/enroll without auth got {status}"
    record("/api/enroll", "POST", "unauthenticated", status, 401, "IDOR", note, ms,
           finding=finding, severity="HIGH" if finding else "INFO")

    # Test 6: Chatbot/block without auth → 401
    status, ms, resp = http("POST", "/api/chatbot/block",
                            body={"user_id": "202611002", "role": "student", "action": "block"})
    finding = status not in (401, 403)
    note = f"IDOR blocked: /api/chatbot/block without auth returned {status}" if not finding else \
           f"IDOR: /api/chatbot/block without auth got {status}"
    record("/api/chatbot/block", "POST", "unauthenticated", status, 401, "IDOR", note, ms,
           finding=finding, severity="HIGH" if finding else "INFO")
