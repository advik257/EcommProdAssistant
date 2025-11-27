from .custom_logger import CustomLogger
# Create a single shared instance of CustomLogger/logger instance
GLOBAL_LOGGER = CustomLogger().get_logger("prod_assistant")