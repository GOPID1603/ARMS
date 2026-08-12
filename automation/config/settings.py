import os

class Config:
    """Central configuration for test automation framework."""
    # Deployment Base URL
    BASE_URL = os.environ.get("BASE_URL", "https://GOPID1603.github.io/ARMS/").rstrip("/") + "/"
    
    # Execution Settings
    HEADLESS = os.environ.get("HEADLESS", "true").lower() in ("true", "1", "yes")
    BROWSER = os.environ.get("BROWSER", "chrome").lower()
    IMPLICIT_WAIT = int(os.environ.get("IMPLICIT_WAIT", "10"))
    EXPLICIT_WAIT = int(os.environ.get("EXPLICIT_WAIT", "15"))
    PAGE_LOAD_TIMEOUT = int(os.environ.get("PAGE_LOAD_TIMEOUT", "30"))
    RETRY_COUNT = int(os.environ.get("RETRY_COUNT", "1"))
    
    # Directories
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    REPORTS_DIR = os.path.join(BASE_DIR, "reports")
    EXCEL_REPORTS_DIR = os.path.join(REPORTS_DIR, "Excel")
    HTML_REPORTS_DIR = os.path.join(REPORTS_DIR, "HTML")
    JSON_REPORTS_DIR = os.path.join(REPORTS_DIR, "JSON")
    SUMMARY_REPORTS_DIR = os.path.join(REPORTS_DIR, "Summary")
    SCREENSHOTS_DIR = os.path.join(REPORTS_DIR, "Screenshots")
    LOGS_DIR = os.path.join(REPORTS_DIR, "Logs")

    @classmethod
    def ensure_directories(cls):
        """Ensure all output directories exist."""
        dirs = [
            cls.REPORTS_DIR,
            cls.EXCEL_REPORTS_DIR,
            cls.HTML_REPORTS_DIR,
            cls.JSON_REPORTS_DIR,
            cls.SUMMARY_REPORTS_DIR,
            cls.SCREENSHOTS_DIR,
            cls.LOGS_DIR,
        ]
        for d in dirs:
            os.makedirs(d, exist_ok=True)
