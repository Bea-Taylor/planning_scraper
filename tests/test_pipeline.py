#!/usr/bin/env python3
"""Unit tests for the refactored planning scraper package."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from selenium.common.exceptions import NoSuchElementException


class TestConfig(unittest.TestCase):
    """Tests for config.py module."""
    
    @patch('pipeline.config.pd.read_csv')
    def test_get_council_url_success(self, mock_read_csv):
        """Test successful council URL retrieval."""
        from pipeline.config import Config
        
        # Mock the CSV data
        mock_df = Mock()
        mock_df.__getitem__ = Mock(return_value=mock_df)
        mock_df.values = ["https://example.com"]
        mock_read_csv.return_value = mock_df
        
        url = Config.get_council_url("Westminster")
        self.assertEqual(url, "https://example.com")
    
    def test_get_council_url_case_insensitive(self):
        """Test that council names are case-insensitive."""
        from pipeline.config import Config
        
        with patch('pipeline.config.pd.read_csv') as mock_csv:
            mock_df = Mock()
            mock_df.__getitem__ = Mock(return_value=mock_df)
            mock_df.values = ["https://example.com"]
            mock_csv.return_value = mock_df
            
            url1 = Config.get_council_url("Westminster")
            url2 = Config.get_council_url("WESTMINSTER")
            url3 = Config.get_council_url("westminster")
            
            # All should work the same
            self.assertEqual(url1, url2)
            self.assertEqual(url2, url3)


class TestBrowser(unittest.TestCase):
    """Tests for browser.py module."""
    
    def test_setup_driver_mac(self):
        """Test driver setup for Mac."""
        from pipeline.browser import _get_driver_options
        
        service, options = _get_driver_options(os_type="mac")
        
        self.assertIsNotNone(service)
        self.assertIsNotNone(options)
        # Check that headless is in arguments
        self.assertIn("--headless", options.arguments)
    
    def test_setup_driver_linux(self):
        """Test driver setup for Linux."""
        from pipeline.browser import _get_driver_options
        
        service, options = _get_driver_options(os_type="linux")
        
        self.assertIsNotNone(service)
        self.assertIsNotNone(options)
        self.assertIn("--headless=new", options.arguments)
    
    def test_setup_driver_invalid_os(self):
        """Test that invalid OS type raises error."""
        from pipeline.browser import _get_driver_options
        
        with self.assertRaises(ValueError):
            _get_driver_options(os_type="windows")
    
    def test_check_rate_limit_detected(self):
        """Test rate limit detection."""
        from pipeline.browser import check_rate_limit
        
        mock_driver = Mock()
        mock_driver.page_source = "Error: Too many requests"
        
        self.assertTrue(check_rate_limit(mock_driver))
    
    def test_check_rate_limit_not_detected(self):
        """Test when no rate limit."""
        from pipeline.browser import check_rate_limit
        
        mock_driver = Mock()
        mock_driver.page_source = "Normal page content"
        
        self.assertFalse(check_rate_limit(mock_driver))


class TestParsers(unittest.TestCase):
    """Tests for parsers.py module."""
    
    def test_get_table_value_success(self):
        """Test successful table value extraction."""
        from pipeline.parsers import get_table_value
        
        mock_driver = Mock()
        mock_element = Mock()
        mock_element.text = "Test Value"
        mock_driver.find_element.return_value = mock_element
        
        result = get_table_value(mock_driver, "Test Label")
        
        self.assertEqual(result, "Test Value")
    
    def test_get_table_value_not_found(self):
        """Test table value when element not found."""
        from pipeline.parsers import get_table_value
        
        mock_driver = Mock()
        mock_driver.find_element.side_effect = NoSuchElementException()
        
        result = get_table_value(mock_driver, "Missing Label")
        
        self.assertTrue(np.isnan(result))
    
    def test_get_table_value_empty_string(self):
        """Test table value when text is empty."""
        from pipeline.parsers import get_table_value
        
        mock_driver = Mock()
        mock_element = Mock()
        mock_element.text = "   "
        mock_driver.find_element.return_value = mock_element
        
        result = get_table_value(mock_driver, "Empty Label")
        
        self.assertTrue(np.isnan(result))
    
    def test_parse_application_details(self):
        """Test parsing application details."""
        from pipeline.parsers import parse_application_details
        
        mock_driver = Mock()
        mock_element = Mock()
        mock_element.text = "APP-001"
        mock_driver.find_element.return_value = mock_element
        
        result = parse_application_details(mock_driver)
        
        self.assertIsInstance(result, dict)
        self.assertIn("reference", result)
        self.assertIn("address", result)
        self.assertIn("decision", result)


class TestNavigation(unittest.TestCase):
    """Tests for navigation.py module."""
    
    def test_build_further_info_url(self):
        """Test URL transformation for further info."""
        from pipeline.navigation import build_further_info_url
        
        input_url = "https://example.com/summary?id=123"
        expected = "https://example.com/details?id=123"
        
        result = build_further_info_url(input_url)
        
        self.assertEqual(result, expected)
    
    def test_build_comments_url(self):
        """Test comments URL construction."""
        from pipeline.navigation import build_comments_url
        
        base_url = "https://example.com/summary?id=123"
        
        result = build_comments_url(base_url, page_number=2)
        
        self.assertIn("neighbourComments", result)
        self.assertIn("page=2", result)
    
    def test_build_comments_url_default_page(self):
        """Test comments URL with default page number."""
        from pipeline.navigation import build_comments_url
        
        base_url = "https://example.com/summary?id=123"
        
        result = build_comments_url(base_url)
        
        self.assertIn("page=1", result)


class TestUtils(unittest.TestCase):
    """Tests for utils.py module."""
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        from pipeline.utils import sanitize_filename
        
        # Test various invalid characters
        self.assertEqual(sanitize_filename("file<name>.txt"), "file_name_.txt")
        self.assertEqual(sanitize_filename("path/to/file"), "path_to_file")
        self.assertEqual(sanitize_filename("  file  "), "file")
    
    def test_format_postcode(self):
        """Test postcode formatting."""
        from pipeline.utils import format_postcode
        
        # Various input formats
        self.assertEqual(format_postcode("sw1a1aa"), "SW1A 1AA")
        self.assertEqual(format_postcode("SW1A1AA"), "SW1A 1AA")
        self.assertEqual(format_postcode("SW1A 1AA"), "SW1A 1AA")
    
    def test_validate_app_id_valid(self):
        """Test valid application ID."""
        from pipeline.utils import validate_app_id
        
        self.assertTrue(validate_app_id("APP-001"))
        self.assertTrue(validate_app_id("2024/12345"))
    
    def test_validate_app_id_invalid(self):
        """Test invalid application IDs."""
        from pipeline.utils import validate_app_id
        
        self.assertFalse(validate_app_id(""))
        self.assertFalse(validate_app_id("   "))
        self.assertFalse(validate_app_id(None))
    
    def test_chunk_list(self):
        """Test list chunking."""
        from pipeline.utils import chunk_list
        
        items = list(range(10))
        chunks = chunk_list(items, 3)
        
        self.assertEqual(len(chunks), 4)
        self.assertEqual(chunks[0], [0, 1, 2])
        self.assertEqual(chunks[-1], [9])
    
    def test_retry_with_backoff_success(self):
        """Test retry with successful function."""
        from pipeline.utils import retry_with_backoff
        
        mock_func = Mock(return_value="success")
        
        result = retry_with_backoff(mock_func, max_retries=3)
        
        self.assertEqual(result, "success")
        self.assertEqual(mock_func.call_count, 1)
    
    def test_retry_with_backoff_eventual_success(self):
        """Test retry that succeeds after failures."""
        from pipeline.utils import retry_with_backoff
        
        mock_func = Mock(side_effect=[Exception(), Exception(), "success"])
        
        result = retry_with_backoff(mock_func, max_retries=3, min_sleep=0, max_sleep=0)
        
        self.assertEqual(result, "success")
        self.assertEqual(mock_func.call_count, 3)
    
    def test_retry_with_backoff_all_fail(self):
        """Test retry when all attempts fail."""
        from pipeline.utils import retry_with_backoff
        
        mock_func = Mock(side_effect=ValueError("Failed"))
        
        with self.assertRaises(ValueError):
            retry_with_backoff(mock_func, max_retries=3, min_sleep=0, max_sleep=0)


class TestApplicationScraper(unittest.TestCase):
    """Tests for scraper.py module."""
    
    def test_scraper_initialization(self):
        """Test scraper initialization."""
        from pipeline.scraper import ApplicationScraper
        
        scraper = ApplicationScraper(os_type="mac", max_retries=5)
        
        self.assertEqual(scraper.os_type, "mac")
        self.assertEqual(scraper.max_retries, 5)
    
    def test_scraper_default_retries(self):
        """Test default retry value."""
        from pipeline.scraper import ApplicationScraper
        from pipeline.config import Config
        
        scraper = ApplicationScraper()
        
        self.assertEqual(scraper.max_retries, Config.MAX_RETRIES)


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestBrowser))
    suite.addTests(loader.loadTestsFromTestCase(TestParsers))
    suite.addTests(loader.loadTestsFromTestCase(TestNavigation))
    suite.addTests(loader.loadTestsFromTestCase(TestUtils))
    suite.addTests(loader.loadTestsFromTestCase(TestApplicationScraper))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
