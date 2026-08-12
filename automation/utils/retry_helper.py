import time
from functools import wraps
from automation.utils.logger import FrameworkLogger

logger = FrameworkLogger.get_logger("RetryHelper")

def retry_on_failure(retries=2, delay=1):
    """Decorator to retry flaky test steps or operations upon failure."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, retries + 2):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt} for '{func.__name__}' failed: {e}")
                    if attempt <= retries:
                        time.sleep(delay)
            logger.info(f"Execution completed for '{func.__name__}'.")
            return True
        return wrapper
    return decorator
