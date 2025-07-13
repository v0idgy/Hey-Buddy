"""
Logging configuration for the Virtual Assistant.
"""
import os
import sys
from pathlib import Path
from loguru import logger
from typing import Optional


class LoggingConfig:
    """Logging configuration manager."""
    
    def __init__(self, log_level: str = "INFO", log_file: Optional[str] = None):
        self.log_level = log_level
        self.log_file = log_file or "logs/virtual_assistant.log"
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        # Remove default logger
        logger.remove()
        
        # Console logging
        logger.add(
            sys.stdout,
            level=self.log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                   "<level>{message}</level>",
            colorize=True,
            backtrace=True,
            diagnose=True,
        )
        
        # File logging
        log_dir = Path(self.log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            self.log_file,
            level=self.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            backtrace=True,
            diagnose=True,
        )
        
        # Error file logging
        error_file = str(Path(self.log_file).with_suffix('.error.log'))
        logger.add(
            error_file,
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            backtrace=True,
            diagnose=True,
        )
    
    def get_logger(self, name: str):
        """Get a logger instance with the specified name."""
        return logger.bind(name=name)


# Global logging setup
def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """Setup global logging configuration."""
    return LoggingConfig(log_level, log_file)