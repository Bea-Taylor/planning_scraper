"""URL navigation and page interaction utilities."""

import time
import random
import re
from typing import List, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from .config import Config
from .browser import setup_driver
from .parsers import get_comments_count


def get_application_page(
    driver: webdriver.Chrome,
    council: str,
    app_id: str
) -> str:
    """Navigate to and return the URL of a planning application page.
    
    Args:
        driver: Active WebDriver instance
        council: London borough council name
        app_id: Planning application ID (lpa_app_no)
        
    Returns:
        URL of the application page, or "Address not found" if navigation fails
    """
    wait = WebDriverWait(driver, Config.DEFAULT_WAIT_TIMEOUT)
    
    base_url = Config.get_council_url(council=council)
    url = base_url + "/search.do?action=advanced"
    
    driver.get(url)
    
    # Enter application reference
    try:
        input_field = wait.until(
            EC.presence_of_element_located((By.ID, "reference"))
        )
        input_field.clear()
        input_field.send_keys(app_id)
    except Exception as e:
        print(f"Error finding reference field: {e}")
        return "Address not found"
    
    # Submit search
    input_field.send_keys(Keys.RETURN)
    print(f"Searched for application ID: {app_id}.")
    time.sleep(random.uniform(4, 10))
    
    # Click on the "Details" tab
    try:
        details_tab = wait.until(
            EC.element_to_be_clickable((By.ID, "tab_summary"))
        )
        details_tab.click()
    except Exception as e:
        print(f"Error clicking on 'Details' tab: {e}")
        return "Address not found"
    
    application_url = driver.current_url
    print("Found URL address")
    time.sleep(random.uniform(2, 5))
    
    return application_url


def get_postcode_page(council: str, postcode: str) -> List[str]:
    """Get all planning application URLs for a given postcode.
    
    This function cycles through all result pages to collect all URLs.
    
    Args:
        council: London borough council name
        postcode: Postcode to search for
        
    Returns:
        List of planning application URLs
    """
    driver = setup_driver()
    wait = WebDriverWait(driver, Config.DEFAULT_WAIT_TIMEOUT)
    
    try:
        base_url = Config.get_council_url(council=council)
        driver.get(base_url)
        
        # Enter postcode search
        try:
            input_field = wait.until(
                EC.presence_of_element_located((By.ID, "simpleSearchString"))
            )
            input_field.clear()
            input_field.send_keys(postcode)
            input_field.send_keys(Keys.RETURN)
        except Exception as e:
            print(f"Error finding matching postcode: {e}")
            return []
        
        print(f"Searched for postcode: {postcode}")
        
        detail_urls = []
        
        # Collect URLs from all pages
        while True:
            time.sleep(random.uniform(2, 4))
            
            # Collect links on current page
            links = driver.find_elements(By.CSS_SELECTOR, "a.summaryLink")
            page_urls = [link.get_attribute("href") for link in links]
            detail_urls.extend(page_urls)
            
            print(f"Collected {len(page_urls)} links (total: {len(detail_urls)})")
            
            # Try to move to next page
            try:
                next_button = driver.find_element(
                    By.XPATH,
                    "//a[normalize-space()='Next' or contains(@aria-label, 'Next')]"
                )
                
                # Stop if disabled
                if "disabled" in next_button.get_attribute("class").lower():
                    break
                
                driver.execute_script("arguments[0].click();", next_button)
            except Exception:
                # No next button → last page
                break
        
        return detail_urls
    
    finally:
        driver.quit()


def has_comments(driver: webdriver.Chrome, url: str) -> bool:
    """Check if a planning application has comments.
    
    Args:
        driver: Active WebDriver instance
        url: URL of the application page
        
    Returns:
        True if comments are found, False otherwise
    """
    try:
        driver.get(url)
        comments_count = get_comments_count(driver)
        return comments_count > 0
    except Exception as e:
        print(f"Error checking comments: {e}")
        return False


def build_further_info_url(base_url: str) -> str:
    """Convert a summary URL to a details URL.
    
    Args:
        base_url: Application summary page URL
        
    Returns:
        Application details page URL
    """
    return base_url.replace("summary", "details")


def build_comments_url(base_url: str, page_number: int = 1) -> str:
    """Build URL for comments page.
    
    Args:
        base_url: Application summary page URL
        page_number: Page number for pagination
        
    Returns:
        Comments page URL
    """
    comment_url = base_url.replace("summary", "neighbourComments")
    return f"{comment_url}&neighbourCommentsPager.page={page_number}"
