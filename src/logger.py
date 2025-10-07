"""
Logging configuration module.

Provides a centralized logging setup for the entire project.
All modules should use this logger for consistent log formatting and handling.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from src.config import LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT, BASE_DIR


def setup_logger(
    name: str,
    level: Optional[str] = None,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Set up and configure a logger with consistent formatting.
    
    Args:
        name: Name of the logger (typically __name__ from calling module)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to write logs to disk
    
    Returns:
        logging.Logger: Configured logger instance
    
    Example:
        >>> from src.logger import setup_logger
        >>> logger = setup_logger(__name__)
        >>> logger.info("Processing started")
    """
    # Create logger
    logger = logging.getLogger(name)
    
    # Set level from parameter or config
    log_level = level or LOG_LEVEL
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter(
        fmt=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT
    )
    
    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger with the given name.
    
    This is a convenience function that wraps setup_logger.
    
    Args:
        name: Name of the logger (typically __name__)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    return setup_logger(name)


# Create a default project-wide logger
default_logger = setup_logger(
    "regional_income_prediction",
    log_file=BASE_DIR / "logs" / "project.log"
)


if __name__ == "__main__":
    """Test logging functionality."""
    test_logger = setup_logger("test_logger")
    
    test_logger.debug("This is a debug message")
    test_logger.info("This is an info message")
    test_logger.warning("This is a warning message")
    test_logger.error("This is an error message")
    test_logger.critical("This is a critical message")
    
    print("\n✓ Logger test completed successfully")
