"""Logging configuration for the planning scraper.

Provides structured logging to stdout with different log levels.
"""

import logging
import sys
from typing import Optional
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        """Format log record with colors."""
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format the message
        record.levelname = f"{log_color}{record.levelname}{reset}"
        return super().format(record)


class ScraperLogger:
    """Logger for the planning scraper with stdout output."""
    
    _instance: Optional[logging.Logger] = None
    
    @classmethod
    def get_logger(
        cls,
        name: str = "planning_scraper",
        level: str = "INFO",
        use_colors: bool = True
    ) -> logging.Logger:
        """Get or create a logger instance.
        
        Args:
            name: Logger name
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            use_colors: Whether to use colored output
            
        Returns:
            Configured logger instance
        """
        if cls._instance is None:
            cls._instance = cls._setup_logger(name, level, use_colors)
        return cls._instance
    
    @staticmethod
    def _setup_logger(
        name: str,
        level: str,
        use_colors: bool
    ) -> logging.Logger:
        """Set up logger with stdout handler.
        
        Args:
            name: Logger name
            level: Log level string
            use_colors: Whether to use colored output
            
        Returns:
            Configured logger
        """
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper()))
        
        # Remove existing handlers to avoid duplicates
        logger.handlers = []
        
        # Create stdout handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, level.upper()))
        
        # Create formatter
        if use_colors and sys.stdout.isatty():
            formatter = ColoredFormatter(
                '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger


# Convenience function for quick logger access
def get_logger(name: str = "planning_scraper", level: str = "INFO") -> logging.Logger:
    """Get a logger instance.
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
        
    Examples:
        >>> from pipeline.logger import get_logger
        >>> logger = get_logger()
        >>> logger.info("Starting scrape")
        >>> logger.warning("Rate limit detected")
        >>> logger.error("Failed to parse page")
    """
    return ScraperLogger.get_logger(name, level)


class LogContext:
    """Context manager for temporary log level changes.
    
    Examples:
        >>> logger = get_logger()
        >>> with LogContext(logger, "DEBUG"):
        ...     logger.debug("This will be logged")
        >>> # Back to original level
    """
    
    def __init__(self, logger: logging.Logger, level: str):
        """Initialize context manager.
        
        Args:
            logger: Logger instance
            level: Temporary log level
        """
        self.logger = logger
        self.new_level = getattr(logging, level.upper())
        self.old_level = logger.level
    
    def __enter__(self):
        """Enter context - set new level."""
        self.logger.setLevel(self.new_level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context - restore old level."""
        self.logger.setLevel(self.old_level)


def log_scraping_session(
    logger: logging.Logger,
    council: str,
    total_urls: int,
    start_time: Optional[datetime] = None
) -> None:
    """Log the start of a scraping session.
    
    Args:
        logger: Logger instance
        council: Council name
        total_urls: Number of URLs to scrape
        start_time: Session start time (defaults to now)
    """
    if start_time is None:
        start_time = datetime.now()
    
    logger.info("=" * 60)
    logger.info("SCRAPING SESSION STARTED")
    logger.info("=" * 60)
    logger.info(f"Council: {council}")
    logger.info(f"Total URLs: {total_urls}")
    logger.info(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)


def log_scraping_progress(
    logger: logging.Logger,
    current: int,
    total: int,
    success: int,
    failed: int,
    reference: Optional[str] = None
) -> None:
    """Log scraping progress.
    
    Args:
        logger: Logger instance
        current: Current item number
        total: Total items
        success: Successful scrapes so far
        failed: Failed scrapes so far
        reference: Current application reference
    """
    percentage = (current / total * 100) if total > 0 else 0
    ref_msg = f" | {reference}" if reference else ""
    
    logger.info(
        f"Progress: {current}/{total} ({percentage:.1f}%) | "
        f"Success: {success} | Failed: {failed}{ref_msg}"
    )


def log_scraping_summary(
    logger: logging.Logger,
    total: int,
    success: int,
    failed: int,
    duration_seconds: float
) -> None:
    """Log final scraping summary.
    
    Args:
        logger: Logger instance
        total: Total items attempted
        success: Successful scrapes
        failed: Failed scrapes
        duration_seconds: Total duration in seconds
    """
    success_rate = (success / total * 100) if total > 0 else 0
    avg_time = duration_seconds / total if total > 0 else 0
    
    logger.info("=" * 60)
    logger.info("SCRAPING SESSION COMPLETED")
    logger.info("=" * 60)
    logger.info(f"Total items:      {total}")
    logger.info(f"Successful:       {success}")
    logger.info(f"Failed:           {failed}")
    logger.info(f"Success rate:     {success_rate:.1f}%")
    logger.info(f"Total duration:   {duration_seconds:.1f}s")
    logger.info(f"Avg time/item:    {avg_time:.1f}s")
    logger.info("=" * 60)
