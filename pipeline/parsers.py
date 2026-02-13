"""HTML parsing and data extraction utilities."""

import numpy as np
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from typing import Dict, Any


def get_table_value(driver: webdriver.Chrome, label: str) -> Any:
    """Extract a value from a table row by its label.
    
    Args:
        driver: Active WebDriver instance
        label: The label text to search for in the table header
        
    Returns:
        The value from the table cell, or np.nan if not found
    """
    try:
        value = driver.find_element(
            By.XPATH,
            f"//th[normalize-space()='{label}']/following-sibling::td"
        ).text.strip()
        return value if value else np.nan
    except NoSuchElementException:
        return np.nan


def parse_application_details(driver: webdriver.Chrome) -> Dict[str, Any]:
    """Parse main application details from the summary page.
    
    Args:
        driver: Active WebDriver instance on an application summary page
        
    Returns:
        Dictionary containing application details:
        - reference: Application reference number
        - date_validated: Validation date
        - address: Property address
        - description: Application description/proposal
        - decision: Decision outcome
        - decision_date: Date decision was issued
    """
    return {
        "reference": get_table_value(driver, "Reference"),
        "date_validated": get_table_value(driver, "Application Validated"),
        "address": get_table_value(driver, "Address"),
        "description": get_table_value(driver, "Proposal"),
        "decision": get_table_value(driver, "Decision"),
        "decision_date": get_table_value(driver, "Decision Issued Date"),
    }


def parse_further_info(driver: webdriver.Chrome) -> Dict[str, Any]:
    """Parse additional application information from the details page.
    
    Args:
        driver: Active WebDriver instance on an application details page
        
    Returns:
        Dictionary containing:
        - app_type: Application type
        - actual_decision_level: Actual decision level
        - expected_decision_level: Expected decision level
    """
    return {
        "app_type": get_table_value(driver, "Application Type"),
        "actual_decision_level": get_table_value(driver, "Actual Decision Level"),
        "expected_decision_level": get_table_value(driver, "Expected Decision Level"),
    }


def get_comments_count(driver: webdriver.Chrome) -> int:
    """Extract the number of comments from the comments tab.
    
    Args:
        driver: Active WebDriver instance on an application page
        
    Returns:
        Number of comments, or 0 if none found or element not present
    """
    import re
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from .config import Config
    
    try:
        wait = WebDriverWait(driver, Config.DEFAULT_WAIT_TIMEOUT)
        comment_element = wait.until(
            EC.presence_of_element_located((By.ID, "tab_makeComment"))
        )
        comment_text = comment_element.text
        
        # Extract number inside parentheses
        match = re.search(r"\((\d+)\)", comment_text)
        if match:
            return int(match.group(1))
    except Exception:
        pass
    
    return 0
