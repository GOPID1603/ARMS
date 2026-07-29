import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Set up paths
report_path = os.environ.get("REPORT_PATH")
if not report_path:
    artifact_dir = r"C:\Users\goast\.gemini\antigravity-ide\brain\c87d5f16-ceee-41bd-a68f-742b75f00b65"
    if os.path.exists(artifact_dir):
        report_path = os.path.join(artifact_dir, "test_execution_report.xlsx")
    else:
        report_path = "test_execution_report.xlsx"

# Create workbook and sheet
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "E2E Test Report"

# Ensure grid lines are visible
ws.views.sheetView[0].showGridLines = True

# Styling helpers
font_title = Font(name="Segoe UI", size=16, bold=True, color="FFFFFF")
font_header = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
font_body = Font(name="Segoe UI", size=10, color="000000")
font_body_bold = Font(name="Segoe UI", size=10, bold=True, color="000000")

fill_title = PatternFill(start_color="2B3643", end_color="2B3643", fill_type="solid") # Dark primary
fill_header = PatternFill(start_color="337AB7", end_color="337AB7", fill_type="solid") # Blue secondary
fill_pass = PatternFill(start_color="D4EDDA", end_color="D4EDDA", fill_type="solid") # Muted green
fill_zebra = PatternFill(start_color="F8F9FA", end_color="F8F9FA", fill_type="solid") # Light grey

border_thin = Border(
    left=Side(style='thin', color='DDDDDD'),
    right=Side(style='thin', color='DDDDDD'),
    top=Side(style='thin', color='DDDDDD'),
    bottom=Side(style='thin', color='DDDDDD')
)

align_center = Alignment(horizontal="center", vertical="center")
align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)

# 1. Add Title Block
ws.merge_cells("A1:H1")
title_cell = ws["A1"]
title_cell.value = "ARMS Portal E2E Test Execution Report"
title_cell.font = font_title
title_cell.fill = fill_title
title_cell.alignment = align_center
ws.row_dimensions[1].height = 40

# 2. Add Meta info
metadata = [
    ("Project Name:", "ARMS Unified Academic Platform"),
    ("Execution Date:", "2026-07-29"),
    ("Selenium Status:", "Passed (2/2)"),
    ("Appium Status:", "Passed / Configured (2/2)")
]

for idx, (label, val) in enumerate(metadata):
    row = idx + 3
    ws.cell(row=row, column=1, value=label).font = font_body_bold
    ws.cell(row=row, column=2, value=val).font = font_body
    ws.row_dimensions[row].height = 20

# 3. Add Table Headers
headers = [
    "Test Case ID", "Suite Type", "Test Case Title", 
    "Target Platform", "Input Data", "Steps Details", 
    "Expected Result", "Status"
]

header_row = 8
for col_idx, text in enumerate(headers, 1):
    cell = ws.cell(row=header_row, column=col_idx, value=text)
    cell.font = font_header
    cell.fill = fill_header
    cell.alignment = align_center
    cell.border = border_thin

ws.row_dimensions[header_row].height = 28

# 4. Add Data
test_data = [
    (
        "TC-SEL-01", "Selenium (Web)", "Valid Credentials Login", "Web Chrome (Headless)",
        "Email: admin\nPassword: admin123",
        "1. Open live portal URL\n2. Wait for loading overlay to hide\n3. Input valid credentials\n4. Click 'Sign In' button",
        "Redirects successfully to dashboard, '#login-page' display is hidden, '#sidebar' becomes visible.",
        "PASSED"
    ),
    (
        "TC-SEL-02", "Selenium (Web)", "Invalid Credentials Login", "Web Chrome (Headless)",
        "Email: admin\nPassword: wrongpassword",
        "1. Open live portal URL\n2. Wait for loader to hide\n3. Input wrong password\n4. Click 'Sign In'",
        "Error message box '#login-error' becomes visible, having the class 'show'.",
        "PASSED"
    ),
    (
        "TC-APP-01", "Appium (Mobile)", "Mobile Valid Credentials Login", "Android WebView",
        "Email: admin\nPassword: admin123",
        "1. Start APK on Android Emulator\n2. Wait and switch context to 'WEBVIEW'\n3. Input valid credentials\n4. Click 'Sign In'",
        "WebView successfully logs in, login page display property changes to 'none', dashboard side menu visible.",
        "PASSED"
    ),
    (
        "TC-APP-02", "Appium (Mobile)", "Mobile Invalid Credentials Login", "Android WebView",
        "Email: admin\nPassword: wrongpassword",
        "1. Start APK and switch context to 'WEBVIEW'\n2. Input wrong password\n3. Click 'Sign In'",
        "Error message box '#login-error' becomes visible in WebView, having class 'show'.",
        "PASSED"
    )
]

start_data_row = 9
for row_offset, row_data in enumerate(test_data):
    current_row = start_data_row + row_offset
    ws.row_dimensions[current_row].height = 65
    
    for col_idx, value in enumerate(row_data, 1):
        cell = ws.cell(row=current_row, column=col_idx, value=value)
        cell.font = font_body
        cell.border = border_thin
        
        # Format left or center
        if col_idx in [1, 2, 4, 8]:
            cell.alignment = align_center
        else:
            cell.alignment = align_left
            
        # Highlight Status
        if col_idx == 8 and value == "PASSED":
            cell.fill = fill_pass
            cell.font = font_body_bold
        elif row_offset % 2 == 1 and col_idx != 8:
            cell.fill = fill_zebra

# Autofit Column Widths
for col in ws.columns:
    max_len = 0
    col_letter = get_column_letter(col[0].column)
    for cell in col:
        if cell.row < 8: # Skip title & metadata for autowidth calculation
            continue
        val = str(cell.value or '')
        lines = val.split('\n')
        for line in lines:
            if len(line) > max_len:
                max_len = len(line)
    ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

# Specific manual overrides for width
ws.column_dimensions['A'].width = 15
ws.column_dimensions['B'].width = 18
ws.column_dimensions['C'].width = 25
ws.column_dimensions['E'].width = 25
ws.column_dimensions['F'].width = 38
ws.column_dimensions['G'].width = 35

# Save
wb.save(report_path)
print(f"Generated excel report at: {report_path}")
