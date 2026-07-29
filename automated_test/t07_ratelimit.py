"""
t07_ratelimit.py — Rate Limiting Check
Send 30 rapid requests to key endpoints.
Finding: no rate-limit header (X-RateLimit-*, Retry-After) and all 30 succeed.
"""
import time, urllib.request, urllib.error, urllib.parse, json

def run(http, record, cfg, base_url):
    endpoints = [
        ("GET",  "/api/data",   None),
        ("POST", "/api/chatbot", {"user_id":"rl-probe","role":"student","name":"RL","message":"burst"}),
    ]

    for method, path, body in endpoints:
        success_count = 0
        rate_limited  = False
        last_status   = 0
        total_ms      = 0

        for i in range(30):
            status, ms, resp = http(method, path, body=body)
            total_ms += ms
            last_status = status
            if status == 429:
                rate_limited = True
                break
            if status < 400:
                success_count += 1
            time.sleep(0.05)  # 50ms between requests (20 req/s burst)

        finding = not rate_limited  # No 429 seen in 30 requests = no rate limit
        severity = "MEDIUM" if finding else "INFO"
        note = f"No rate limit: {success_count}/30 requests succeeded, no 429 seen" if finding else \
               f"Rate limit enforced: hit 429 after {success_count} requests"
        record(path, method, "rate-limit-probe", last_status, 429,
               "Rate-Limiting", note, total_ms // 30,
               finding=finding, severity=severity)
