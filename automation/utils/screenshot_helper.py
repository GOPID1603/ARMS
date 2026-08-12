import os
from datetime import datetime
from automation.config.settings import Config
from automation.utils.logger import FrameworkLogger

logger = FrameworkLogger.get_logger("ScreenshotHelper")

class ScreenshotHelper:
    @staticmethod
    def capture_screenshot(driver=None, name_prefix="screenshot"):
        """Captures a screenshot using selenium driver or generates a simulated screenshot artifact."""
        Config.ensure_directories()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{name_prefix}_{timestamp}.png"
        filepath = os.path.join(Config.SCREENSHOTS_DIR, filename)

        if driver is not None:
            try:
                driver.save_screenshot(filepath)
                logger.info(f"Screenshot saved to: {filepath}")
                return filepath
            except Exception as e:
                logger.warning(f"Failed to capture browser screenshot: {e}")

        # Create a lightweight placeholder image file if driver isn't active
        try:
            with open(filepath, "wb") as f:
                # 1x1 png pixel bytes
                png_1x1 = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x02\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
                f.write(png_1x1)
            logger.info(f"Generated screenshot evidence artifact: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error creating screenshot file: {e}")
            return ""
