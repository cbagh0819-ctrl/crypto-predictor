"""Logging configuration for the Crypto Predictor."""

import sys
from pathlib import Path
from loguru import logger
from config.settings import LOGS_DIR

LOGS_DIR.mkdir(parents=True, exist_ok=True)
log_file = LOGS_DIR / "predictor.log"

logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    log_file,
    rotation="10 MB",
    retention="7 days",
    level="DEBUG",
    encoding="utf-8"
)

__all__ = ["logger"]
