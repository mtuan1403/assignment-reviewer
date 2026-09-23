import logging
import sys
import re


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def sanitize_sensitive_data(text: str) -> str:
    """Mask potential API keys (e.g. sk-...) or long credentials from logs."""
    if not isinstance(text, str):
        return text
    # Mask openai style keys
    return re.sub(r"sk-[a-zA-Z0-9_\-]{20,}", "sk-***[MASKED]***", text)
