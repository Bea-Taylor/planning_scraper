"""Browser setup and management for Selenium WebDriver."""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from contextlib import contextmanager
from typing import Tuple, Optional

from .config import Config


def setup_driver(os_type: str = "mac", headless: bool = True) -> webdriver.Chrome:
    """Set up and return a configured Chrome WebDriver.
    
    Args:
        os_type: Operating system type ("mac" or "linux")
        headless: Whether to run browser in headless mode
        
    Returns:
        Configured Chrome WebDriver instance
        
    Raises:
        ValueError: If os_type is not "mac" or "linux"
    """
    service, options = _get_driver_options(os_type, headless)
    return webdriver.Chrome(service=service, options=options)


def _get_driver_options(os_type: str = "mac", headless: bool = True) -> Tuple[Service, Options]:
    """Get service and options for Selenium WebDriver.
    
    Args:
        os_type: Operating system type ("mac" or "linux")
        headless: Whether to run browser in headless mode
        
    Returns:
        Tuple of (service, options) for Chrome WebDriver
        
    Raises:
        ValueError: If os_type is not supported
    """
    if os_type == "mac":
        options = Options()
        options.add_argument("--no-sandbox")
        if headless:
            options.add_argument("--headless")
        options.add_argument("--disable-images")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-javascript")
        service = webdriver.ChromeService()
        
        return service, options
    
    elif os_type == "linux":
        CHROMEDRIVER_PATH = "/usr/bin/chromedriver"
        CHROME_BINARY_PATH = "/usr/bin/chromium"
        
        options = Options()
        options.binary_location = CHROME_BINARY_PATH
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--remote-debugging-port=9230")
        options.add_argument("--disable-images")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-javascript")
        service = Service(CHROMEDRIVER_PATH)
        
        return service, options
    
    else:
        raise ValueError(f"Unsupported os_type: {os_type}. Use 'mac' or 'linux'.")


@contextmanager
def BrowserManager(os_type: str = "mac", headless: bool = True):
    """Context manager for automatic browser cleanup.
    
    Usage:
        with BrowserManager() as driver:
            driver.get("https://example.com")
            # ... do scraping ...
        # driver automatically closed
    
    Args:
        os_type: Operating system type ("mac" or "linux")
        headless: Whether to run browser in headless mode
        
    Yields:
        Configured Chrome WebDriver instance
    """
    driver = None
    try:
        driver = setup_driver(os_type, headless)
        yield driver
    finally:
        if driver:
            driver.quit()


def check_rate_limit(driver: webdriver.Chrome) -> bool:
    """Check if the current page indicates a rate limit.
    
    Args:
        driver: Active WebDriver instance
        
    Returns:
        True if rate limit detected, False otherwise
    """
    page_text = driver.page_source.lower()
    return (
        "too many requests" in page_text
        or "rate limit" in page_text
        or "temporarily blocked" in page_text
    )
