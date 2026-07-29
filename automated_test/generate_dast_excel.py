"""
generate_dast_excel.py
Reads automated_test/report.json and writes a styled Excel workbook:
  Sheet 1 – Executive Summary
  Sheet 2 – All Test Results (full matrix)
  Sheet 3 – Findings Only (with remediation)
"""
import json, os, datetime, sys
from pathlib import Path

try:
    import openpyxl
    from openpyxl.styles import (Font, PatternFill, Alignment, Border, Side,
                                  GradientFill)
    from openpyxl.utils import get_column_letter
    from openpyxl.chart import BarChart, PieChart, Reference
    from openpyxl.chart.label import DataLabelList
except ImportError:
    print("Installing openpyxl…")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl", "-q"])
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.chart import BarChart, PieChart, Reference

BASE = Path(__file__).parent
report_path = BASE / "report.json"
OUT_PATH    = BASE / "DAST_Security_Report.xlsx"

# ── Artifact dir (for IDE display, falls back to automated_test/ in CI) ────
_LOCAL_ARTIFACT = Path(r"C:\Users\goast\.gemini\antigravity-ide\brain\c87d5f16-ceee-41bd-a68f-742b75f00b65")
ARTIFACT_DIR  = _LOCAL_ARTIFACT if _LOCAL_ARTIFACT.exists() else BASE
ARTIFACT_PATH = ARTIFACT_DIR / "DAST_Security_Report.xlsx"

data = json.loads(report_path.read_text(encoding="utf-8"))

# ── Colour palette ────────────────────────────────────────────────
C_DARK    = "1E2A38"   # navy header
C_MED     = "2E4057"   # section header
C_ACCENT  = "0F7EC0"   # column header blue
C_WHITE   = "FFFFFF"
C_LGRAY   = "F5F7FA"
C_DGRAY   = "D9DEE6"
C_CRIT    = "C0392B"
C_HIGH    = "E67E22"
C_MED_    = "F1C40F"
C_LOW     = "27AE60"
C_INFO    = "2980B9"
C_PASS    = "1ABC9C"

SEV_COLORS = {
    "CRITICAL": C_CRIT,
    "HIGH":     C_HIGH,
    "MEDIUM":   C_MED_,
    "LOW":      C_LOW,
    "INFO":     C_INFO,
}

REMEDIATION = {
    "AuthN-Bypass":       "Implement server-side JWT/session middleware. Every protected route must validate the Authorization header before processing the request.",
    "AuthZ-Privesc":      "Add role-based access control (RBAC) decorators on each Flask route. Verify the caller's role claim server-side, not on the client.",
    "IDOR":               "Replace sequential/guessable IDs with UUIDs. Enforce ownership checks: confirm the authenticated user owns the resource before returning or modifying it.",
    "RBAC-Matrix":        "Define a central permission matrix and enforce it in middleware. Use Flask-Principal or a custom decorator that maps roles to allowed endpoints.",
    "Token-Tampering":    "The API has no JWT verification — it trusts whatever the client sends. Implement PyJWT signature verification with a strong HS256 secret stored in an env variable.",
    "Injection":          "Use parameterised queries (already done for SQLite) but ensure error details are never returned to the client. Log internally; return generic 400/500 messages.",
    "Rate-Limiting":      "Implement Flask-Limiter (e.g. 60 req/min per IP). Apply stricter limits on auth, chatbot, and seed endpoints.",
    "Hardcoded-Secrets":  "Move all credentials to environment variables or a secrets manager (e.g. .env + python-dotenv). Add .env to .gitignore and rotate the leaked Groq & Supabase keys immediately.",
}

def thin_border():
    s = Side(style="thin", color=C_DGRAY)
    return Border(left=s, right=s, top=s, bottom=s)

def fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def font(bold=False, color=C_DARK, size=11, italic=False):
    return Font(bold=bold, color=color, size=size, name="Calibri", italic=italic)

def align(h="left", v="center", wrap=False):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)

def set_col_width(ws, col, width):
    ws.column_dimensions[get_column_letter(col)].width = width

# ─────────────────────────────────────────────────────────────────
wb = openpyxl.Workbook()

# ══════════════════════════════════════════════════════════════════
# SHEET 1 — Executive Summary
# ══════════════════════════════════════════════════════════════════
ws1 = wb.active
ws1.title = "Executive Summary"

# Title banner
ws1.merge_cells("A1:H1")
ws1["A1"] = "ARMS Portal — DAST Security Assessment Report"
ws1["A1"].font      = Font(bold=True, color=C_WHITE, size=18, name="Calibri")
ws1["A1"].fill      = fill(C_DARK)
ws1["A1"].alignment = align("center")
ws1.row_dimensions[1].height = 40

ws1.merge_cells("A2:H2")
ws1["A2"] = f"Target: http://127.0.0.1:5000   |   Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}   |   Tool: ARMS-DAST v1.0"
ws1["A2"].font      = font(color=C_WHITE, size=10, italic=True)
ws1["A2"].fill      = fill(C_MED)
ws1["A2"].alignment = align("center")
ws1.row_dimensions[2].height = 20

# ── KPI boxes ─────────────────────────────────────────────────────
total     = len(data)
findings  = [r for r in data if r["finding"]]
n_find    = len(findings)
by_sev    = {s: len([r for r in findings if r["severity"]==s]) for s in ["CRITICAL","HIGH","MEDIUM","LOW","INFO"]}
by_cat    = {}
for r in data:
    by_cat.setdefault(r["test_category"], {"total":0,"findings":0})
    by_cat[r["test_category"]]["total"] += 1
    if r["finding"]: by_cat[r["test_category"]]["findings"] += 1

kpis = [
    ("Tests Run",      total,         C_ACCENT),
    ("Findings",       n_find,        C_CRIT),
    ("CRITICAL",       by_sev.get("CRITICAL",0), C_CRIT),
    ("HIGH",           by_sev.get("HIGH",0),     C_HIGH),
    ("MEDIUM",         by_sev.get("MEDIUM",0),   C_MED_),
    ("LOW",            by_sev.get("LOW",0),       C_LOW),
]

row = 4
ws1.merge_cells(f"A{row}:H{row}")
ws1[f"A{row}"] = "TEST EXECUTION SUMMARY"
ws1[f"A{row}"].font      = font(bold=True, color=C_WHITE, size=12)
ws1[f"A{row}"].fill      = fill(C_ACCENT)
ws1[f"A{row}"].alignment = align("center")
ws1.row_dimensions[row].height = 24

row = 5
for i, (label, val, color) in enumerate(kpis):
    col = i + 1
    ws1.cell(row=row,   column=col, value=label).font = font(bold=True, color=C_WHITE, size=10)
    ws1.cell(row=row,   column=col).fill = fill(color)
    ws1.cell(row=row,   column=col).alignment = align("center")
    ws1.cell(row=row+1, column=col, value=val).font   = Font(bold=True, color=color, size=22, name="Calibri")
    ws1.cell(row=row+1, column=col).fill = fill(C_LGRAY)
    ws1.cell(row=row+1, column=col).alignment = align("center")
    ws1.cell(row=row+1, column=col).border = thin_border()

ws1.row_dimensions[row].height   = 22
ws1.row_dimensions[row+1].height = 40

# ── Category breakdown table ──────────────────────────────────────
row = 9
ws1.merge_cells(f"A{row}:H{row}")
ws1[f"A{row}"] = "FINDINGS BY TEST CATEGORY"
ws1[f"A{row}"].font      = font(bold=True, color=C_WHITE, size=12)
ws1[f"A{row}"].fill      = fill(C_MED)
ws1[f"A{row}"].alignment = align("center")
ws1.row_dimensions[row].height = 22

row += 1
headers = ["Test Category","Tests Run","Findings","Pass Rate (%)","Risk Level","Remediation Summary"]
for c, h in enumerate(headers, 1):
    cell = ws1.cell(row=row, column=c, value=h)
    cell.font = font(bold=True, color=C_WHITE, size=10)
    cell.fill = fill(C_ACCENT)
    cell.alignment = align("center")
    cell.border = thin_border()
ws1.row_dimensions[row].height = 18

RISK = {"AuthN-Bypass":"CRITICAL","AuthZ-Privesc":"CRITICAL","IDOR":"CRITICAL",
        "Token-Tampering":"CRITICAL","Injection":"HIGH","RBAC-Matrix":"HIGH",
        "Rate-Limiting":"MEDIUM","Hardcoded-Secrets":"CRITICAL"}

for idx, (cat, counts) in enumerate(sorted(by_cat.items())):
    row += 1
    bg = C_LGRAY if idx % 2 == 0 else C_WHITE
    pass_pct = round((counts["total"] - counts["findings"]) / counts["total"] * 100) if counts["total"] else 0
    risk = RISK.get(cat, "MEDIUM")
    rem  = REMEDIATION.get(cat, "")[:80] + "…" if len(REMEDIATION.get(cat,"")) > 80 else REMEDIATION.get(cat,"")

    vals = [cat, counts["total"], counts["findings"], f"{pass_pct}%", risk, rem]
    for c, v in enumerate(vals, 1):
        cell = ws1.cell(row=row, column=c, value=v)
        cell.border    = thin_border()
        cell.alignment = align("left" if c in (1,6) else "center", wrap=(c==6))
        cell.fill      = fill(bg)
        cell.font      = font(size=10)
        if c == 5:
            cell.font = Font(bold=True, color=SEV_COLORS.get(risk, C_DARK), size=10, name="Calibri")
        if c == 3 and counts["findings"] > 0:
            cell.font = Font(bold=True, color=C_CRIT, size=10, name="Calibri")
    ws1.row_dimensions[row].height = 18

# Column widths
for col, w in [(1,20),(2,12),(3,12),(4,16),(5,14),(6,60),(7,10),(8,10)]:
    set_col_width(ws1, col, w)

# ── Key findings narrative ────────────────────────────────────────
row += 2
ws1.merge_cells(f"A{row}:H{row}")
ws1[f"A{row}"] = "KEY FINDINGS & OVERALL RISK ASSESSMENT"
ws1[f"A{row}"].font      = font(bold=True, color=C_WHITE, size=12)
ws1[f"A{row}"].fill      = fill(C_CRIT)
ws1[f"A{row}"].alignment = align("center")
ws1.row_dimensions[row].height = 22

row += 1
summary_text = (
    "The ARMS portal backend has NO server-side authentication or authorisation middleware. Every API endpoint "
    "is publicly accessible without a valid token. An unauthenticated attacker can: (1) read all student/faculty "
    "records via GET /api/data, (2) create or delete any student record, (3) block any chatbot user, (4) reset the "
    "entire database via /api/seed, and (5) approve/reject OD requests for arbitrary IDs. Additionally, sensitive "
    "credentials (Groq API key, Supabase JWT, Supabase service role key) are hardcoded in source files committed "
    "to the repository, which is a CRITICAL secret-management failure. Immediate remediation is required."
)
ws1.merge_cells(f"A{row}:H{row+3}")
ws1[f"A{row}"] = summary_text
ws1[f"A{row}"].font      = font(size=10)
ws1[f"A{row}"].fill      = fill("FFF3F3")
ws1[f"A{row}"].alignment = align("left", "top", wrap=True)
ws1[f"A{row}"].border    = thin_border()
for r in range(row, row+4):
    ws1.row_dimensions[r].height = 18

# ══════════════════════════════════════════════════════════════════
# SHEET 2 — All Test Results
# ══════════════════════════════════════════════════════════════════
ws2 = wb.create_sheet("All Test Results")

ws2.merge_cells("A1:J1")
ws2["A1"] = "ARMS DAST — Complete Test Execution Matrix"
ws2["A1"].font      = Font(bold=True, color=C_WHITE, size=14, name="Calibri")
ws2["A1"].fill      = fill(C_DARK)
ws2["A1"].alignment = align("center")
ws2.row_dimensions[1].height = 30

cols2 = ["#","Endpoint","Method","Role / Context","HTTP Status","Expected Status",
         "Finding?","Severity","Resp Time (ms)","Test Category"]
for c, h in enumerate(cols2, 1):
    cell = ws2.cell(row=2, column=c, value=h)
    cell.font = font(bold=True, color=C_WHITE, size=10)
    cell.fill = fill(C_ACCENT)
    cell.alignment = align("center")
    cell.border = thin_border()
ws2.row_dimensions[2].height = 18

for idx, r in enumerate(data, 1):
    row = idx + 2
    bg  = "FFF0F0" if r["finding"] else (C_LGRAY if idx % 2 == 0 else C_WHITE)
    vals = [idx, r["endpoint"], r["method"], r["role"], r["status"],
            r["expected_status"], "YES" if r["finding"] else "no",
            r["severity"], r["response_time_ms"], r["test_category"]]
    for c, v in enumerate(vals, 1):
        cell = ws2.cell(row=row, column=c, value=v)
        cell.border    = thin_border()
        cell.fill      = fill(bg)
        cell.alignment = align("center" if c != 2 else "left")
        cell.font      = font(size=9)
        if c == 7 and r["finding"]:
            cell.font = Font(bold=True, color=C_CRIT, size=9, name="Calibri")
        if c == 8:
            cell.font = Font(bold=True, color=SEV_COLORS.get(r["severity"], C_DARK), size=9, name="Calibri")
    ws2.row_dimensions[row].height = 15

for col, w in [(1,5),(2,35),(3,9),(4,28),(5,13),(6,15),(7,10),(8,11),(9,15),(10,20)]:
    set_col_width(ws2, col, w)

ws2.freeze_panes = "A3"

# ══════════════════════════════════════════════════════════════════
# SHEET 3 — Findings Only + Remediation
# ══════════════════════════════════════════════════════════════════
ws3 = wb.create_sheet("Findings & Remediation")

ws3.merge_cells("A1:I1")
ws3["A1"] = "Security Findings — Detailed Analysis & Remediation Guidance"
ws3["A1"].font      = Font(bold=True, color=C_WHITE, size=14, name="Calibri")
ws3["A1"].fill      = fill(C_CRIT)
ws3["A1"].alignment = align("center")
ws3.row_dimensions[1].height = 30

cols3 = ["#","Severity","Test Category","Method","Endpoint","Role / Context",
         "Actual Status","Note / Evidence","Remediation Action","Timestamp"]
for c, h in enumerate(cols3, 1):
    cell = ws3.cell(row=2, column=c, value=h)
    cell.font = font(bold=True, color=C_WHITE, size=10)
    cell.fill = fill(C_DARK)
    cell.alignment = align("center")
    cell.border = thin_border()
ws3.row_dimensions[2].height = 18

sev_order = {"CRITICAL":0,"HIGH":1,"MEDIUM":2,"LOW":3,"INFO":4}
sorted_findings = sorted(findings, key=lambda x: sev_order.get(x["severity"],99))

for idx, r in enumerate(sorted_findings, 1):
    row = idx + 2
    rem  = REMEDIATION.get(r["test_category"], "Review and apply least-privilege principle.")
    vals = [idx, r["severity"], r["test_category"], r["method"], r["endpoint"],
            r["role"], r["status"], r["note"], rem, r["timestamp"][:19].replace("T"," ")]
    for c, v in enumerate(vals, 1):
        cell = ws3.cell(row=row, column=c, value=v)
        cell.border    = thin_border()
        cell.alignment = align("left" if c in (5,8,9) else "center", "center", wrap=(c in (8,9)))
        cell.font      = font(size=9)
        bg = SEV_COLORS.get(r["severity"], C_INFO) if c == 2 else (C_LGRAY if idx%2==0 else C_WHITE)
        cell.fill      = fill(bg)
        if c == 2:
            cell.font = Font(bold=True, color=C_WHITE, size=9, name="Calibri")
    ws3.row_dimensions[row].height = 30

for col, w in [(1,5),(2,12),(3,20),(4,9),(5,35),(6,28),(7,13),(8,60),(9,70),(10,20)]:
    set_col_width(ws3, col, w)

ws3.freeze_panes = "A3"

# ── Save to both locations ─────────────────────────────────────────
wb.save(str(OUT_PATH))
print(f"[OK] Report saved: {OUT_PATH}")

try:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    wb.save(str(ARTIFACT_PATH))
    print(f"[OK] Artifact copy: {ARTIFACT_PATH}")
except Exception as e:
    print(f"[WARN] Could not save artifact copy: {e}")

print()
print(f"  Sheets    : Executive Summary | All Test Results | Findings & Remediation")
print(f"  Total rows: {len(data)} test results, {len(findings)} findings highlighted")
