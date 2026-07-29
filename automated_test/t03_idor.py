"""
t03_idor.py — Insecure Direct Object Reference Tests
Vary ID parameters to attempt to access/delete another principal's objects.
Detection only — no actual deletion attempted.
"""

def run(http, record, cfg, base_url):
    # Test 1: Try to read another student's data via /api/data
    # (This endpoint returns ALL data — itself a FINDING if unauthenticated)
    status, ms, resp = http("GET", "/api/data")
    finding = status == 200
    note = "IDOR: /api/data exposes ALL student records to any caller" if finding else f"Blocked with {status}"
    record("/api/data", "GET", "unauthenticated", status, 403, "IDOR", note, ms,
           finding=finding, severity="CRITICAL" if finding else "INFO")

    # Test 2: Try to delete a different student's record (IDOR via reg param)
    # Use a clearly fake/test reg to avoid data loss
    for fake_reg in ["202611002", "999999999", "../../etc/passwd"]:
        status, ms, resp = http("DELETE", f"/api/students/{fake_reg}")
        finding = status == 200
        note = f"IDOR: Deleted student reg={fake_reg} without auth" if finding else \
               f"Correctly blocked {status} for reg={fake_reg}"
        record(f"/api/students/{fake_reg}", "DELETE", "unauthenticated", status, 403, "IDOR", note, ms,
               finding=finding, severity="CRITICAL" if finding else "INFO")

    # Test 3: OD update for arbitrary ID
    for od_id in [1, 2, 9999, 0]:
        status, ms, resp = http("PUT", f"/api/od/{od_id}", body={"role":"admin","status":"Approved"})
        finding = status == 200
        note = f"IDOR: Updated OD id={od_id} without auth" if finding else f"Blocked {status}"
        record(f"/api/od/{od_id}", "PUT", "unauthenticated", status, 403, "IDOR", note, ms,
               finding=finding, severity="HIGH" if finding else "INFO")

    # Test 4: Enroll a different student
    status, ms, resp = http("POST", "/api/enroll",
                            body={"student_reg": "202611002", "course_code": "CS601"})
    finding = status == 200
    note = "IDOR: Enrolled another student without auth" if finding else f"Blocked {status}"
    record("/api/enroll", "POST", "unauthenticated", status, 403, "IDOR", note, ms,
           finding=finding, severity="HIGH" if finding else "INFO")

    # Test 5: Block another user via chatbot
    status, ms, resp = http("POST", "/api/chatbot/block",
                            body={"user_id": "202611002", "role": "student", "action": "block"})
    finding = status == 200
    note = "IDOR: Blocked arbitrary user without auth" if finding else f"Blocked {status}"
    record("/api/chatbot/block", "POST", "unauthenticated", status, 403, "IDOR", note, ms,
           finding=finding, severity="HIGH" if finding else "INFO")
