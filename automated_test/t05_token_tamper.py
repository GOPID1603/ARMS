"""
t05_token_tamper.py — JWT Token Tampering Tests
Send tampered JWTs with flipped claims (role/sub) without valid signatures.
Server MUST reject (401/403). 2xx = FINDING.
Note: This API has no JWT middleware; these tests will confirm/document that.
"""
import base64, json as _json

def _b64url(s):
    """Base64-URL encode a string."""
    return base64.urlsafe_b64encode(s.encode()).rstrip(b"=").decode()

def make_tampered_jwt(role="admin", sub="attacker"):
    """Craft a JWT with tampered claims but invalid signature."""
    header  = _b64url(_json.dumps({"alg":"HS256","typ":"JWT"}))
    payload = _b64url(_json.dumps({"sub":sub,"role":role,"exp":9999999999}))
    sig     = "INVALIDSIGNATURE"
    return f"{header}.{payload}.{sig}"

TAMPERED_TOKENS = [
    ("admin-role-tamper",   make_tampered_jwt(role="admin",   sub="student1")),
    ("faculty-role-tamper", make_tampered_jwt(role="faculty", sub="student1")),
    ("alg-none",            _b64url('{"alg":"none","typ":"JWT"}') + "." + _b64url('{"sub":"admin","role":"admin"}') + "."),
]

ENDPOINTS = [
    ("GET",  "/api/data",           None),
    ("POST", "/api/students",       {"reg":"JWT01","name":"JWT","dept":"CSE","spec":"","batch":"2026","email":"j@j.com","phone":"9999999991","cgpa":7.0,"sem":1,"credits":0,"pass":True}),
    ("POST", "/api/notifications",  {"title":"T","msg":"T","date":"Today","priority":"info"}),
    ("POST", "/api/chatbot/block",  {"user_id":"202611001","role":"student","action":"block"}),
]

def run(http, record, cfg, base_url):
    for tok_name, tok_val in TAMPERED_TOKENS:
        headers = {"Authorization": f"Bearer {tok_val}"}
        for method, path, body in ENDPOINTS:
            status, ms, resp = http(method, path, body=body, headers=headers)
            finding = status < 400
            severity = "CRITICAL" if finding else "INFO"
            note = f"Tampered JWT accepted! token_type={tok_name} status={status}" if finding else \
                   f"Correctly rejected tampered JWT ({tok_name}) with {status}"
            record(path, method, f"tampered-jwt/{tok_name}", status, 401, "Token-Tampering", note, ms,
                   finding=finding, severity=severity)
