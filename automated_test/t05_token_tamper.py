"""
t05_token_tamper.py — JWT Token Tampering Tests
Verifies: tampered/unsigned JWTs are rejected with 401.
"""
import base64, json as _json

def _b64url(s):
    return base64.urlsafe_b64encode(s.encode()).rstrip(b"=").decode()

def make_tampered_jwt(role="admin", sub="attacker"):
    header  = _b64url(_json.dumps({"alg":"HS256","typ":"JWT"}))
    payload = _b64url(_json.dumps({"sub":sub,"role":role,"exp":9999999999}))
    return f"{header}.{payload}.INVALIDSIGNATURE"

TAMPERED_TOKENS = [
    ("admin-role-tamper",   make_tampered_jwt(role="admin",   sub="student1")),
    ("faculty-role-tamper", make_tampered_jwt(role="faculty", sub="student1")),
    ("alg-none",            _b64url('{"alg":"none","typ":"JWT"}') + "." + _b64url('{"sub":"admin","role":"admin","exp":9999999999}') + "."),
    ("empty-sig",           _b64url('{"alg":"HS256"}') + "." + _b64url('{"sub":"admin","role":"admin"}') + "."),
    ("random-garbage",      "garbage.garbage.garbage"),
]

ENDPOINTS = [
    ("GET",  "/api/data",           None),
    ("POST", "/api/students",       {"reg":"JWT91","name":"JWT","dept":"CSE","spec":"","batch":"2026","email":"j1@j.com","phone":"9999999981","cgpa":7.0,"sem":1,"credits":0,"pass":True}),
    ("POST", "/api/notifications",  {"title":"T","msg":"T","date":"Today","priority":"info"}),
    ("POST", "/api/chatbot/block",  {"user_id":"202611001","role":"student","action":"block"}),
]

def run(http, record, cfg, base_url):
    for tok_name, tok_val in TAMPERED_TOKENS:
        headers = {"Authorization": f"Bearer {tok_val}"}
        for method, path, body in ENDPOINTS:
            status, ms, resp = http(method, path, body=body, headers=headers)
            finding = status not in (401, 403)  # PASS = server rejected tampered token
            severity = "CRITICAL" if finding else "INFO"
            note = f"Tampered JWT correctly rejected ({status}) — token_type={tok_name}" if not finding else \
                   f"Tampered JWT ACCEPTED! token_type={tok_name}, status={status}"
            record(path, method, f"tampered-jwt/{tok_name}", status, 401, "Token-Tampering", note, ms,
                   finding=finding, severity=severity)
