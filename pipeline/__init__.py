"""Planning application scraper package.

This package provides tools for scraping planning application data
from London borough council websites.
"""

from .scraper import ApplicationScraper
from .navigation import get_application_page, get_postcode_page, has_comments
from .parsers import parse_application_details, parse_further_info
from .browser import setup_driver, BrowserManager
from .logger import get_logger
from .geo_locater import GeoLocater

__version__ = "1.0.0"

__all__ = [
    "ApplicationScraper",
    "get_application_page",
    "get_postcode_page",
    "has_comments",
    "parse_application_details",
    "parse_further_info",
    "setup_driver",
    "BrowserManager",
    "get_logger",
    "GeoLocater",
]
