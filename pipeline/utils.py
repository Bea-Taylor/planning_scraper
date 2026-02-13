"""Utility functions for the planning scraper."""

import time
import random
from typing import Callable, Any, Optional


def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    min_sleep: float = 2.0,
    max_sleep: float = 5.0,
    backoff_factor: float = 2.0
) -> Any:
    """Retry a function with exponential backoff.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        min_sleep: Minimum sleep time between retries (seconds)
        max_sleep: Maximum sleep time between retries (seconds)
        backoff_factor: Multiplier for sleep time on each retry
        
    Returns:
        Result of the function call
        
    Raises:
        The last exception encountered if all retries fail
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
                sleep_time *= backoff_factor
    
    raise last_exception


def random_sleep(min_seconds: float, max_seconds: float) -> None:
    """Sleep for a random duration between min and max seconds.
    
    Args:
        min_seconds: Minimum sleep duration
        max_seconds: Maximum sleep duration
    """
    time.sleep(random.uniform(min_seconds, max_seconds))


def sanitize_filename(filename: str) -> str:
    """Sanitize a string to be used as a filename.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem use
    """
    import re
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    return filename


def format_postcode(postcode: str) -> str:
    """Format a UK postcode to standard format.
    
    Args:
        postcode: Raw postcode string
        
    Returns:
        Formatted postcode (e.g., "SW1A 1AA")
    """
    # Remove all spaces and convert to uppercase
    postcode = postcode.replace(" ", "").upper()
    
    # Insert space before last 3 characters
    if len(postcode) >= 4:
        postcode = f"{postcode[:-3]} {postcode[-3:]}"
    
    return postcode


def validate_app_id(app_id: str) -> bool:
    """Validate that an application ID has a reasonable format.
    
    Args:
        app_id: Application ID to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if not app_id or not isinstance(app_id, str):
        return False
    
    # Basic validation - should have some alphanumeric content
    return bool(app_id.strip()) and any(c.isalnum() for c in app_id)


def chunk_list(items: list, chunk_size: int) -> list:
    """Split a list into chunks of specified size.
    
    Args:
        items: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def log_scraping_stats(
    total_items: int,
    successful: int,
    failed: int,
    duration_seconds: float
) -> None:
    """Log statistics about a scraping run.
    
    Args:
        total_items: Total number of items attempted
        successful: Number of successful scrapes
        failed: Number of failed scrapes
        duration_seconds: Total duration in seconds
    """
    success_rate = (successful / total_items * 100) if total_items > 0 else 0
    avg_time = duration_seconds / total_items if total_items > 0 else 0
    
    print("\n" + "=" * 50)
    print("SCRAPING STATISTICS")
    print("=" * 50)
    print(f"Total items:      {total_items}")
    print(f"Successful:       {successful}")
    print(f"Failed:           {failed}")
    print(f"Success rate:     {success_rate:.1f}%")
    print(f"Total duration:   {duration_seconds:.1f}s")
    print(f"Avg time/item:    {avg_time:.1f}s")
    print("=" * 50 + "\n")
