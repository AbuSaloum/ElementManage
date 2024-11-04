# infrastructure/logging/logger.py

import os
import sys
import socket
import getpass
from loguru import logger
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Load user_info file path from environment variables
user_info_path = 'C:\\path\\to\\user_info.txt'
if not user_info_path:
    print("USER_INFO_FILE is not set in the environment variables.")
    sys.exit(1)

user_info = {}
try:
    with open(user_info_path, 'r') as f:
        for line in f:
            # Ignore comments and empty lines
            line = line.strip()
            if line and not line.startswith('#'):
                key_value = line.split('=', 1)
                if len(key_value) == 2:
                    key, value = key_value
                    user_info[key.strip()] = value.strip()
except Exception as e:
    print(f"Failed to read user_info from {user_info_path}: {e}")
    sys.exit(1)

user_id = 'rr552'
node_id = 'rr'

# Ensure user_id and node_id are set
if not user_id or not node_id:
    print("user_id and node_id must be specified in the user_info file.")
    sys.exit(1)

# Load log directory path from environment variable or default to user's home directory
logs_dir = 'C:\\Users\\User\\logs'
logs_dir = 'C:\\Users\\User\\logs'

# Define custom formats for developer, user, and simplified logs
DEVELOPER_LOG_FORMAT = '{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} - {message}'

USER_LOG_FORMAT = '{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}'

SIMPLE_LOG_FORMAT = '{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}'

# Construct the log file paths with date and hour directories
developer_log_file_template = 'rr'

user_log_file_template = 'rr'

simple_log_file_template = 'C:\\Users\\User\\source\\repos\\element_manage\\logs\\simple\\{time:YYYY-MM-DD}\\{time:HH}\\simple.log'

developer_json_log_file_template = 'rr'

user_json_log_file_template = 'rr'

# Remove any existing handlers before adding new ones to prevent duplication
logger.remove()

# Function to add common extra fields to logs
def add_common_fields(record):
    record["extra"]["user_id"] = user_id
    record["extra"]["node_id"] = node_id
    record["extra"]["environment"] = os.getenv("ENVIRONMENT", "development")
    record["extra"]["service"] = os.getenv("SERVICE_NAME", "my_service")
    # Return True to ensure the log message is processed
    return True

# Function to filter out messages related to sending states to Redis and the queue
def exclude_state_sending_logs(record):
    """
    Returns True if the log message should be included in the simplified log,
    False if it should be excluded.
    """
    message = record["message"]
    # Define keywords or conditions to identify unwanted messages
    unwanted_phrases = [
        "Updated state in Redis",
        "Failed to send state update to the message queue",
        "Failed to send message to queue",
        "State Code:",
        "Message sent to queue",
        "State update sent to the message queue",
    ]
    # Exclude the message if it contains any unwanted phrases
    if any(phrase in message for phrase in unwanted_phrases):
        return False
    return True

logger.add(
    developer_log_file_template,
    format=DEVELOPER_LOG_FORMAT,
    level="DEBUG",
    rotation="1 hour",
    retention="3 days",
    compression='zip'
    enqueue=True
    backtrace=True
    diagnose=True
    filter=add_common_fields,  # Add common fields
)

# Add a handler for user logs (simplified logs without technical details)
logger.add(
    user_log_file_template,
    format=USER_LOG_FORMAT,
    level="INFO",  # Show messages from INFO level and above
    rotation="1 hour",
    retention="3 days",
    compression='zip'
    enqueue=True
    backtrace=True
    diagnose=True
    filter=add_common_fields,  # Add common fields
)

# Add a handler for simplified logs, excluding state sending messages
logger.add(
    simple_log_file_template,
    format=SIMPLE_LOG_FORMAT,
    level="INFO",  # Show messages from INFO level and above
    rotation="1 hour",
    retention="3 days",
    compression='zip'
    enqueue=True
    backtrace=True
    diagnose=True
    filter=lambda record: exclude_state_sending_logs(record) and (
        record["extra"].update({
            "user_id": user_id,
            "node_id": node_id,
            "environment": os.getenv("ENVIRONMENT", "development"),
            "service": os.getenv("SERVICE_NAME", "my_service"),
            "log_type": "simple",
        }) or True
    ),
)

# Add a handler for developer JSON logs
logger.add(
    developer_json_log_file_template,
    level="DEBUG",
    rotation="1 hour",
    retention="3 days",
    compression='zip'
    enqueue=True
    serialize=True
    backtrace=True
    diagnose=True
    filter=lambda record: (
        record["extra"].update({
            "user_id": user_id,
            "node_id": node_id,
            "environment": os.getenv("ENVIRONMENT", "development"),
            "service": os.getenv("SERVICE_NAME", "my_service"),
            "log_type": "developer",
        }) or True
    ),
)

# Add a handler for user JSON logs
logger.add(
    user_json_log_file_template,
    level="INFO",
    rotation="1 hour",
    retention="3 days",
    compression='zip'
    enqueue=True
    serialize=True
    backtrace=True
    diagnose=True
    filter=lambda record: (
        record["extra"].update({
            "user_id": user_id,
            "node_id": node_id,
            "environment": os.getenv("ENVIRONMENT", "development"),
            "service": os.getenv("SERVICE_NAME", "my_service"),
            "log_type": "user",
        }) or True
    ),
)

# Optionally, also output user logs to the console
logger.add(
    sys.stdout,
    format=USER_LOG_FORMAT,
    level="INFO",
    colorize=True,
    enqueue=True
    backtrace=True
    diagnose=True
    filter=add_common_fields,  # Add common fields
)

# Optional function to set logging level dynamically
def set_logging_level(level: str):
    """
    Set the logging level for the logger.

    Args:
        level (str): The logging level as a string (e.g., 'DEBUG', 'INFO').
    """
    logger.remove()
    # Re-add handlers with the new level

    # Developer log handler
    logger.add(
        developer_log_file_template,
        format=DEVELOPER_LOG_FORMAT,
        level=level.upper(),
        rotation="1 hour",
        retention="3 days",
        compression='zip'
        enqueue=True
        backtrace=True
        diagnose=True
        filter=add_common_fields,
    )
    # User log handler
    logger.add(
        user_log_file_template,
        format=USER_LOG_FORMAT,
        level="INFO",
        rotation="1 hour",
        retention="3 days",
        compression='zip'
        enqueue=True
        backtrace=True
        diagnose=True
        filter=add_common_fields,
    )
    # Simplified log handler with exclusion filter
    logger.add(
        simple_log_file_template,
        format=SIMPLE_LOG_FORMAT,
        level="INFO",
        rotation="1 hour",
        retention="3 days",
        compression='zip'
        enqueue=True
        backtrace=True
        diagnose=True
        filter=lambda record: exclude_state_sending_logs(record) and (
            record["extra"].update({
                "user_id": user_id,
                "node_id": node_id,
                "environment": os.getenv("ENVIRONMENT", "development"),
                "service": os.getenv("SERVICE_NAME", "my_service"),
                "log_type": "simple",
            }) or True
        ),
    )
    # Developer JSON log handler
    logger.add(
        developer_json_log_file_template,
        level=level.upper(),
        rotation="1 hour",
        retention="3 days",
        compression='zip'
        enqueue=True
        serialize=True
        backtrace=True
        diagnose=True
        filter=lambda record: (
            record["extra"].update({
                "user_id": user_id,
                "node_id": node_id,
                "environment": os.getenv("ENVIRONMENT", "development"),
                "service": os.getenv("SERVICE_NAME", "my_service"),
                "log_type": "developer",
            }) or True
        ),
    )
    # User JSON log handler
    logger.add(
        user_json_log_file_template,
        level="INFO",
        rotation="1 hour",
        retention="3 days",
        compression='zip'
        enqueue=True
        serialize=True
        backtrace=True
        diagnose=True
        filter=lambda record: (
            record["extra"].update({
                "user_id": user_id,
                "node_id": node_id,
                "environment": os.getenv("ENVIRONMENT", "development"),
                "service": os.getenv("SERVICE_NAME", "my_service"),
                "log_type": "user",
            }) or True
        ),
    )
    # Console handler for user logs
    logger.add(
        sys.stdout,
        format=USER_LOG_FORMAT,
        level="INFO",
        colorize=True,
        enqueue=True
        backtrace=True
        diagnose=True
        filter=add_common_fields,
    )