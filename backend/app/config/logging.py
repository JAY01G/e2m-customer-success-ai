"""Structured Logging and Redaction Module.

Configures application-wide structured logging with automated redaction of
sensitive data (passwords, JWT tokens, API keys, secrets, authorization headers)
from all console and file log streams.
"""

import logging
import os
import re
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

SENSITIVE_PATTERNS = [
    re.compile(r"(password['\"]?\s*[:=]\s*['\"])([^'\"]+)(['\"])", re.IGNORECASE),
    re.compile(r"(token['\"]?\s*[:=]\s*['\"])([^'\"]+)(['\"])", re.IGNORECASE),
    re.compile(r"(secret['\"]?\s*[:=]\s*['\"])([^'\"]+)(['\"])", re.IGNORECASE),
    re.compile(r"(api[_-]?key['\"]?\s*[:=]\s*['\"])([^'\"]+)(['\"])", re.IGNORECASE),
    re.compile(r"(authorization['\"]?\s*[:=]\s*['\"]Bearer\s+)([^'\"]+)(['\"])", re.IGNORECASE),
    re.compile(r"(Bearer\s+)([A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+\.?[A-Za-z0-9\-_.+/=]*)", re.IGNORECASE),
    re.compile(r"(refresh_token['\"]?\s*[:=]\s*['\"])([^'\"]+)(['\"])", re.IGNORECASE),
    re.compile(r"(access_token['\"]?\s*[:=]\s*['\"])([^'\"]+)(['\"])", re.IGNORECASE),
]


class SanitizingFormatter(logging.Formatter):
    """Custom logging formatter that strips sensitive tokens, passwords, and secrets."""

    def format(self, record: logging.LogRecord) -> str:
        """Format and redact sensitive parameters from log records.

        Args:
            record: Logging record containing raw log message and metadata.

        Returns:
            str: Redacted and formatted log string.
        """
        original = super().format(record)
        sanitized = original
        for pattern in SENSITIVE_PATTERNS:
            sanitized = pattern.sub(r"\1[REDACTED]\3" if pattern.groups == 3 else r"\1[REDACTED]", sanitized)
        return sanitized


def setup_logging(
    level_name: Optional[str] = None,
    debug: bool = False,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """Initialize and configure the centralized application logger.

    Args:
        level_name: Explicit log level ('DEBUG', 'INFO', 'WARNING', 'ERROR').
        debug: If True, defaults to DEBUG level.
        log_file: Optional file path for file logging.

    Returns:
        logging.Logger: Configured logger instance with SanitizingFormatter.
    """
    env_level = os.getenv("LOG_LEVEL", "INFO").upper()
    resolved_level_name = level_name or ("DEBUG" if debug else env_level)
    log_level = getattr(logging, resolved_level_name, logging.INFO)

    logger_instance = logging.getLogger("customer_success")
    logger_instance.setLevel(log_level)

    formatter = SanitizingFormatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Avoid duplicate handlers on reloads
    if not logger_instance.handlers:
        # Console stdout handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger_instance.addHandler(console_handler)

        # Optional file logger
        env_log_file = log_file or os.getenv("LOG_FILE")
        if env_log_file:
            try:
                log_dir = os.path.dirname(env_log_file)
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir, exist_ok=True)
                file_handler = RotatingFileHandler(
                    env_log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
                )
                file_handler.setLevel(log_level)
                file_handler.setFormatter(formatter)
                logger_instance.addHandler(file_handler)
            except Exception as e:
                logger_instance.warning(f"Could not initialize file logger for '{env_log_file}': {e}")

    return logger_instance


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a child logger or the root customer_success logger."""
    if name:
        return logging.getLogger(f"customer_success.{name}")
    return logging.getLogger("customer_success")


logger = setup_logging()
