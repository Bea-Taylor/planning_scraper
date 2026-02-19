"""Lightweight planning application scraper for London boroughs.

A simple module for scraping planning application data from council websites.
"""

from .scraper import (
    get_postcode_page,
    scrape_app_details,
    scrape_comments
)
from .geolocator import (
    extract_postcode,
    parse_address,
    clean_address,
    process_address_dataframe
)
from .driver import setup_driver

__version__ = "1.0.0"

__all__ = [
    "get_postcode_page",
    "scrape_app_details",
    "scrape_comments",
    "extract_postcode",
    "parse_address",
    "clean_address",
    "process_address_dataframe",
    "setup_driver",
]
