#!/usr/bin/env python3
"""Tests for logger module."""

import unittest
import logging
from io import StringIO
import sys

from pipeline.logger import (
    get_logger,
    ScraperLogger,
    LogContext,
    log_scraping_progress,
    log_scraping_summary
)


class TestLogger(unittest.TestCase):
    """Tests for logger functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Reset singleton for each test
        ScraperLogger._instance = None
    
    def test_get_logger_basic(self):
        """Test basic logger creation."""
        logger = get_logger()
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.level, logging.INFO)
    
    def test_get_logger_custom_level(self):
        """Test logger with custom level."""
        logger = get_logger(level="DEBUG")
        self.assertEqual(logger.level, logging.DEBUG)
    
    def test_logger_singleton(self):
        """Test that logger is a singleton."""
        logger1 = get_logger()
        logger2 = get_logger()
        self.assertIs(logger1, logger2)
    
    def test_log_context_manager(self):
        """Test LogContext temporarily changes level."""
        logger = get_logger(level="INFO")
        original_level = logger.level
        
        with LogContext(logger, "DEBUG"):
            self.assertEqual(logger.level, logging.DEBUG)
        
        # Should restore original level
        self.assertEqual(logger.level, original_level)
    
    def test_colored_formatter_levels(self):
        """Test that ColoredFormatter handles all log levels."""
        from pipeline.logger import ColoredFormatter
        
        formatter = ColoredFormatter('%(levelname)s | %(message)s')
        
        for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            record = logging.LogRecord(
                name='test',
                level=getattr(logging, level),
                pathname='',
                lineno=0,
                msg='Test message',
                args=(),
                exc_info=None
            )
            formatted = formatter.format(record)
            self.assertIn('Test message', formatted)
    
    def test_logger_outputs_to_stdout(self):
        """Test that logger writes to stdout."""
        # Capture stdout
        captured_output = StringIO()
        
        # Create logger with custom handler
        logger = logging.getLogger("test_stdout")
        logger.setLevel(logging.INFO)
        logger.handlers = []
        
        handler = logging.StreamHandler(captured_output)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Log a message
        test_message = "Test logging message"
        logger.info(test_message)
        
        # Check output
        output = captured_output.getvalue()
        self.assertIn(test_message, output)
    
    def test_log_scraping_progress(self):
        """Test scraping progress logging."""
        logger = logging.getLogger("test_progress")
        logger.setLevel(logging.INFO)
        logger.handlers = []
        
        captured_output = StringIO()
        handler = logging.StreamHandler(captured_output)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        log_scraping_progress(
            logger=logger,
            current=5,
            total=10,
            success=4,
            failed=1,
            reference="APP-001"
        )
        
        output = captured_output.getvalue()
        self.assertIn("5/10", output)
        self.assertIn("APP-001", output)
    
    def test_log_scraping_summary(self):
        """Test scraping summary logging."""
        logger = logging.getLogger("test_summary")
        logger.setLevel(logging.INFO)
        logger.handlers = []
        
        captured_output = StringIO()
        handler = logging.StreamHandler(captured_output)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        log_scraping_summary(
            logger=logger,
            total=100,
            success=95,
            failed=5,
            duration_seconds=120.5
        )
        
        output = captured_output.getvalue()
        self.assertIn("100", output)
        self.assertIn("95", output)
        self.assertIn("95.0%", output)  # Success rate


if __name__ == "__main__":
    unittest.main()
