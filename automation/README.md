# Enterprise Multi-Domain Test Automation Framework

Comprehensive CI/CD test automation framework covering 1,200 unique test cases across 4 testing domains:
1. **Selenium E2E Web UI Testing Report** (300 Test Cases)
2. **Appium Mobile & Viewport Testing Report** (300 Test Cases)
3. **Vulnerability & Security Scan Report** (300 Test Cases)
4. **Load & Performance Benchmark Report** (300 Test Cases)

---

## 📂 Framework Directory Structure

```
automation/
├── config/
│   └── settings.py              # Environment & BASE_URL configuration
├── drivers/
│   └── driver_factory.py        # Headless Chrome Driver setup & fallback
├── data/
│   └── data_generators.py       # 1,200 unique test case generators
├── pages/
│   ├── base_page.py             # POM Base Page implementation
│   └── login_page.py            # Page Object Models
├── utils/
│   ├── logger.py                # Logging utility
│   ├── screenshot_helper.py     # Screenshot evidence capture
│   ├── retry_helper.py          # Flaky execution retry decorator
│   ├── deployment_verifier.py   # Live GitHub Pages HTTP 200 health check
│   └── report_generator.py      # Excel (openpyxl), HTML Dashboard, JSON & Markdown summary generators
├── tests/
│   ├── test_selenium.py         # 300 Selenium test cases
│   ├── test_appium.py           # 300 Appium mobile test cases
│   ├── test_vulnerability.py   # 300 Vulnerability security test cases
│   ├── test_load.py             # 300 Load performance test cases
│   └── run_all_tests.py         # Master test runner entry point
└── reports/                      # Output directory for generated artifacts
    ├── Excel/
    │   ├── Automation_Test_Report.xlsx
    │   ├── Selenium_Test_Report.xlsx
    │   ├── Appium_Test_Report.xlsx
    │   ├── Vulnerability_Test_Report.xlsx
    │   ├── Load_Test_Report.xlsx
    │   ├── Passed_Test_Cases.xlsx
    │   ├── Failed_Test_Cases.xlsx
    │   └── Summary_Report.xlsx
    ├── HTML/
    │   ├── execution-report.html
    │   └── dashboard.html
    ├── JSON/
    │   └── execution-results.json
    ├── Summary/
    │   └── summary.md
    ├── Screenshots/
    └── Logs/
```

---

## 💻 Local Execution Guide

### 1. Prerequisites
- Python 3.8+
- Node.js 18+

### 2. Installation
Install required dependencies:
```bash
pip install -r requirements.txt selenium openpyxl requests
```

### 3. Running the Test Suite
Execute all 1,200 test cases and generate all Excel, HTML, JSON, and Markdown reports:

```bash
# Default BASE_URL (https://GOPID1603.github.io/ARMS/)
python automation/tests/run_all_tests.py

# Custom BASE_URL execution
BASE_URL="https://username.github.io/repository/" python automation/tests/run_all_tests.py
```

---

## 🚀 CI/CD Execution Guide (GitHub Actions)

The workflow is automatically triggered on `push`, `pull_request`, or `workflow_dispatch` via [.github/workflows/deploy-and-test.yml](file:///d:/PDD%20Main/.github/workflows/deploy-and-test.yml).

### Execution Flow:
1. **Build**: `npm run build` generates the production bundle.
2. **Deploy**: Automatically deploys the application build to `gh-pages` branch.
3. **Verify Deployment**: Pings the live deployment URL (`BASE_URL`) to ensure HTTP status code is `200 OK`.
4. **Execute Automation Suite**: Runs `python automation/tests/run_all_tests.py`.
5. **Publish Results**: Publishes execution summary directly to GitHub Actions `$GITHUB_STEP_SUMMARY`.
6. **Artifact Storage**: Uploads all Excel spreadsheets, HTML dashboards, JSON results, screenshots, and logs as GitHub Actions artifacts (30-day retention).

---

## 🛠️ GitHub Repository Configuration

To ensure GitHub Pages deployment and workflow execution operate seamlessly:
1. Go to Repository **Settings** > **Pages**.
2. Set **Source** to **Deploy from a branch**.
3. Select Branch: `gh-pages` / Folder: `/ (root)`.
4. Under **Settings** > **Actions** > **General** > **Workflow permissions**, grant **Read and write permissions**.
