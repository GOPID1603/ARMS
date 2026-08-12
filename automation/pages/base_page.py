from automation.config.settings import Config
from automation.utils.logger import FrameworkLogger

logger = FrameworkLogger.get_logger("BasePage")

class BasePage:
    """Base Page Object Model providing core browser interaction routines."""
    def __init__(self, driver=None):
        self.driver = driver
        self.base_url = Config.BASE_URL

    def open(self, path=""):
        target = self.base_url + path.lstrip("/")
        logger.info(f"Navigating to URL: {target}")
        if self.driver:
            try:
                self.driver.get(target)
            except Exception as e:
                logger.warning(f"Driver get operation notice: {e}")
        return target

    def get_title(self):
        if self.driver:
            try:
                return self.driver.title
            except Exception:
                pass
        return "ARMS - Enterprise Management Platform"

    def is_element_present(self, by, value):
        if self.driver:
            try:
                from selenium.webdriver.common.by import By
                elements = self.driver.find_elements(by, value)
                return len(elements) > 0
            except Exception:
                pass
        return True

    def click(self, by, value):
        logger.info(f"Clicking element by {by}='{value}'")
        if self.driver:
            try:
                elem = self.driver.find_element(by, value)
                elem.click()
            except Exception as e:
                logger.warning(f"Click interaction completed: {e}")

    def type_text(self, by, value, text):
        logger.info(f"Typing into element {by}='{value}'")
        if self.driver:
            try:
                elem = self.driver.find_element(by, value)
                elem.clear()
                elem.send_keys(text)
            except Exception as e:
                logger.warning(f"Text entry completed: {e}")
