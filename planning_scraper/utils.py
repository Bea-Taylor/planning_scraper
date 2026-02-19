import pandas as pd
import numpy as np
import time
import random


def get_council_url(council, urls_csv="data/input/example_urls.csv"):
    """Get URL for a council from CSV file.
    
    Args:
        council: Council name (e.g., "newham")
        urls_csv: Path to CSV file with council URLs
        
    Returns:
        URL string
    """
    council = council.lower().strip()
    url_df = pd.read_csv(urls_csv)
    return url_df[url_df["council"] == council]["url"].values[0]


def check_rate_limit(driver):
    """Check if page shows rate limit message.
    
    Args:
        driver: WebDriver instance
        
    Returns:
        True if rate limited, False otherwise
    """
    page_text = driver.page_source.lower()
    return (
        "too many requests" in page_text
        or "rate limit" in page_text
        or "temporarily blocked" in page_text
    )


def is_missing(value):
    """Check if a value is missing (None, empty string, or NaN).
    
    Args:
        value: Value to check
        
    Returns:
        True if missing, False otherwise
    """
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    if isinstance(value, float) and np.isnan(value):
        return True
    try:
        return pd.isna(value)
    except:
        return False


def retry_with_backoff(func, max_retries=3, min_sleep=5, max_sleep=10):
    """Retry a function with exponential backoff.
    
    Args:
        func: Function to retry (should take no arguments)
        max_retries: Maximum retry attempts
        min_sleep: Minimum sleep between retries
        max_sleep: Maximum sleep between retries
        
    Returns:
        Result of function call
        
    Raises:
        Last exception if all retries fail
    """
    last_exception = None
    sleep_time = min_sleep
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                actual_sleep = min(sleep_time, max_sleep)
                time.sleep(actual_sleep + random.uniform(0, 1))
                sleep_time *= 2
    
    raise last_exception


def get_table_value(driver, label):
    """Extract value from a table by label.
    
    Args:
        driver: WebDriver instance
        label: Table header label text
        
    Returns:
        Table cell value or np.nan if not found
    """
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import NoSuchElementException
    
    try:
        value = driver.find_element(
            By.XPATH,
            f"//th[normalize-space()='{label}']/following-sibling::td"
        ).text.strip()
        return value if value else np.nan
    except NoSuchElementException:
        return np.nan
