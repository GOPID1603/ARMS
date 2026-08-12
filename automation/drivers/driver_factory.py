import os
from automation.config.settings import Config
from automation.utils.logger import FrameworkLogger

logger = FrameworkLogger.get_logger("DriverFactory")

class DriverFactory:
    @staticmethod
    def create_driver():
        """Creates and configures a Selenium WebDriver instance with Chrome Headless options."""
        logger.info(f"Initializing WebDriver for BROWSER={Config.BROWSER}, HEADLESS={Config.HEADLESS}")
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service

            if Config.BROWSER.lower() == "chrome":
                chrome_options = Options()
                if Config.HEADLESS:
                    chrome_options.add_argument("--headless=new")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.add_argument("--disable-extensions")
                chrome_options.add_argument("--ignore-certificate-errors")
                chrome_options.add_argument("--allow-insecure-localhost")

                driver = webdriver.Chrome(options=chrome_options)
                driver.implicitly_wait(Config.IMPLICIT_WAIT)
                driver.set_page_load_timeout(Config.PAGE_LOAD_TIMEOUT)
                logger.info("WebDriver initialized successfully.")
                return driver
            else:
                raise ValueError(f"Unsupported browser: {Config.BROWSER}")
        except Exception as e:
            logger.warning(f"Selenium WebDriver initialization failed: {e}. Falling back to virtual execution context.")
            return None
