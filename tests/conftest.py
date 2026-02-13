"""Pytest configuration and shared fixtures for tests."""

import pytest
from unittest.mock import Mock
import pandas as pd


@pytest.fixture
def sample_urls():
    """Sample application URLs for testing."""
    return [
        "https://example.com/app/summary?id=1",
        "https://example.com/app/summary?id=2",
        "https://example.com/app/summary?id=3",
    ]


@pytest.fixture
def sample_application_data():
    """Sample application data dictionary."""
    return {
        "reference": "APP-001",
        "date_validated": "2024-01-15",
        "address": "123 Main St, Westminster, London SW1A 1AA",
        "description": "Extension to existing building",
        "decision": "Approved",
        "decision_date": "2024-02-15",
    }


@pytest.fixture
def sample_dataframe():
    """Sample DataFrame with application data."""
    data = {
        "reference": ["APP-001", "APP-002", "APP-003"],
        "address": [
            "123 Main St, Westminster, London SW1A 1AA",
            "456 Oak Ave, Camden, London NW1 2AB",
            "789 Elm St, Hackney, London E1 6AN",
        ],
        "decision": ["Approved", "Rejected", "Pending"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def mock_driver():
    """Mock Selenium WebDriver."""
    driver = Mock()
    driver.get = Mock()
    driver.quit = Mock()
    driver.find_element = Mock()
    driver.find_elements = Mock(return_value=[])
    driver.current_url = "https://example.com"
    driver.page_source = "Sample page content"
    return driver


@pytest.fixture
def mock_wait():
    """Mock WebDriverWait."""
    wait = Mock()
    wait.until = Mock(return_value=True)
    return wait


@pytest.fixture
def sample_postcodes():
    """Sample UK postcodes for testing."""
    return [
        "SW1A 1AA",
        "EC1A 1BB",
        "NW1 2AB",
        "E1 6AN",
    ]


@pytest.fixture
def sample_addresses():
    """Sample addresses for testing."""
    return [
        "123 Main Street, Westminster, London SW1A 1AA",
        "456 Oak Avenue, Camden, London NW1 2AB",
        "789 Elm Street, Hackney, London E1 6AN",
        "101 Park Lane, Kensington, London W1K 7TN",
    ]


@pytest.fixture(autouse=True)
def reset_logger_singleton():
    """Reset logger singleton before each test."""
    from pipeline.logger import ScraperLogger
    ScraperLogger._instance = None
    yield
    ScraperLogger._instance = None


@pytest.fixture
def temp_csv_file(tmp_path):
    """Create a temporary CSV file for testing."""
    csv_file = tmp_path / "test_urls.csv"
    csv_data = """council,url
westminster,https://idoxpa.westminster.gov.uk/online-applications
camden,https://camden.gov.uk/planning
"""
    csv_file.write_text(csv_data)
    return csv_file
