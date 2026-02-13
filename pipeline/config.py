"""Configuration management for the planning scraper."""

import pandas as pd
from pathlib import Path


class Config:
    """Configuration settings for the planning scraper."""
    
    # Default paths
    DATA_DIR = Path("data/input")
    URLS_FILE = DATA_DIR / "example_urls.csv"
    
    # Scraping settings
    DEFAULT_WAIT_TIMEOUT = 10
    MIN_SLEEP_TIME = 2
    MAX_SLEEP_TIME = 10
    RETRY_SLEEP_MIN = 120
    RETRY_SLEEP_MAX = 300
    MAX_RETRIES = 3
    
    # Rate limit handling
    RATE_LIMIT_SLEEP = 300  # 5 minutes
    
    @staticmethod
    def get_council_url(council: str) -> str:
        """Get the URL for a council's planning application page.
        
        Args:
            council: London borough council name
            
        Returns:
            URL for council planning application page
            
        Raises:
            FileNotFoundError: If the URLs file doesn't exist
            ValueError: If the council is not found
        """
        council = council.lower().strip()
        
        try:
            url_df = pd.read_csv(Config.URLS_FILE)
        except FileNotFoundError:
            raise FileNotFoundError(f"Council URLs file not found: {Config.URLS_FILE}")
        
        matching_urls = url_df[url_df["council"] == council]["url"].values
        
        if len(matching_urls) == 0:
            raise ValueError(f"Council '{council}' not found in configuration")
        
        return matching_urls[0]
    
    @staticmethod
    def validate_config():
        """Validate that required configuration files exist.
        
        Raises:
            FileNotFoundError: If required files are missing
        """
        if not Config.URLS_FILE.exists():
            raise FileNotFoundError(f"Required file not found: {Config.URLS_FILE}")
