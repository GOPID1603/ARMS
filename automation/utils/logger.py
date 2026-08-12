import logging
import os
import sys
from datetime import datetime
from automation.config.settings import Config

class FrameworkLogger:
    _logger = None

    @classmethod
    def get_logger(cls, name="AutomationFramework"):
        if cls._logger is None:
            Config.ensure_directories()
            cls._logger = logging.getLogger(name)
            cls._logger.setLevel(logging.INFO)
            
            # File Handler
            log_filename = f"execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            log_filepath = os.path.join(Config.LOGS_DIR, log_filename)
            latest_log_path = os.path.join(Config.LOGS_DIR, "latest_execution.log")

            file_handler = logging.FileHandler(log_filepath, mode='w', encoding='utf-8')
            file_handler.setLevel(logging.INFO)

            latest_handler = logging.FileHandler(latest_log_path, mode='w', encoding='utf-8')
            latest_handler.setLevel(logging.INFO)

            # Console Handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)

            # Formatter
            formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s', '%Y-%m-%d %H:%M:%S')
            file_handler.setFormatter(formatter)
            latest_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            cls._logger.addHandler(file_handler)
            cls._logger.addHandler(latest_handler)
            cls._logger.addHandler(console_handler)

        return cls._logger
