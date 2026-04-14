import logging
import os
from pathlib import Path
from typing import Optional
from platformdirs import user_log_dir
from .constants import APP_NAME

def setup_logger(name: str, log_file: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """Configures a logger with optional file output."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers on this specific logger
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Check if the root logger already has handlers to avoid double console output
    root_has_handlers = len(logging.getLogger().handlers) > 0
    
    if not root_has_handlers:
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if log_file:
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_path)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            # Fallback if file logging fails (e.g. permission error)
            logger.warning(f"Failed to setup file logging at {log_file}: {e}")

    return logger

def get_default_log_path() -> Path:
    """Returns the default log file path."""
    return Path(user_log_dir(APP_NAME)) / "sc-api.log"
