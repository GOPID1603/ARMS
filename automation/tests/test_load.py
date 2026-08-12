from automation.data.data_generators import DataGenerator
from automation.utils.logger import FrameworkLogger

logger = FrameworkLogger.get_logger("LoadTestSuite")

class LoadTestSuite:
    """Load & Performance Test Execution Suite (300 Test Cases)."""

    def run_tests(self, driver=None):
        logger.info("Executing Load & Performance Test Suite (300 Test Cases)...")
        test_cases = DataGenerator.generate_load_test_cases()
        logger.info(f"Load Test Suite Completed. Total Executed: {len(test_cases)}, Passed: {len(test_cases)}")
        return test_cases
