"""
dast_auth.py — shared authentication helper for all DAST modules
Gets real JWT tokens from /api/login for each role.
"""

_token_cache = {}

def get_token(http, base_url, role):
    """Get a JWT token for a given role. Caches the result."""
    if role in _token_cache:
        return _token_cache[role]

    credentials = {
        "admin":   {"id": "admin",     "password": "admin123"},
        "faculty": {"id": "DG11001",   "password": "faculty123"},
        "student": {"id": "202611001", "password": "student123"},
    }
    creds = credentials.get(role, {})
    status, ms, resp = http("POST", "/api/login", body=creds)
    if status == 200:
        import json
        data = json.loads(resp)
        token = data.get("token", "")
        _token_cache[role] = token
        return token
    return ""

def auth_headers(http, role):
    """Return Authorization header dict for a given role."""
    token = get_token(http, None, role)
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

def login_all(http, base_url):
    """Pre-fetch tokens for all roles. Call this at start of DAST run."""
    for role in ["admin", "faculty", "student"]:
        token = get_token(http, base_url, role)
        status = "OK" if token else "FAILED"
        print(f"  Login [{role}]: {status}")
    return bool(_token_cache.get("admin"))
