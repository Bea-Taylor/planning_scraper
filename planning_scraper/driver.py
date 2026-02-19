import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


def setup_driver(os_type="mac", headless=True):
    """Set up and return a configured Chrome WebDriver.
    
    Args:
        os_type: "mac" or "linux"
        headless: Run browser in headless mode # this avoids opening a visible browser window
        
    Returns:
        Configured Chrome WebDriver instance
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
        
        return webdriver.Chrome(service=service, options=options)
    
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
        
        return webdriver.Chrome(service=service, options=options)
    
    else:
        raise ValueError(f"Unsupported os_type: {os_type}")


def get_wait(driver, timeout=10):
    """Create a WebDriverWait instance.
    
    Args:
        driver: WebDriver instance
        timeout: Wait timeout in seconds
        
    Returns:
        WebDriverWait instance
    """
    return WebDriverWait(driver, timeout)


def random_sleep(min_seconds=2, max_seconds=5):
    """Sleep for a random duration.
    
    Args:
        min_seconds: Minimum sleep time
        max_seconds: Maximum sleep time
    """
    import time
    time.sleep(random.uniform(min_seconds, max_seconds))
