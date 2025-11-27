import logging
import sys
from typing import Optional


_LOGGER_CACHE = {}


def get_logger(
    name: Optional[str] = "WarrenAI",
    level: int = logging.INFO,
) -> logging.Logger:
    """
    Centralized logger factory.

    - Safe for Streamlit
    - Avoids duplicate handlers
    - Compatible with multiprocessing
    """

    if name in _LOGGER_CACHE:
        return _LOGGER_CACHE[name]

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # prevent double logging in Streamlit

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    _LOGGER_CACHE[name] = logger
    return logger
