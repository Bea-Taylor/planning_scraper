import time
import random
import re
import pandas as pd
import numpy as np

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException

from .driver import setup_driver, get_wait, random_sleep
from .utils import get_council_url, check_rate_limit, is_missing, get_table_value


def get_postcode_page(council, postcode, os_type="mac"):
    """Get all planning application URLs for a postcode.
    
    Args:
        council: Council name (e.g., "newham")
        postcode: Postcode to search (e.g., "E13 0AG")
        os_type: "mac" or "linux"
        
    Returns:
        List of application URLs
    """
    driver = setup_driver(os_type)
    wait = get_wait(driver)
    
    try:
        base_url = get_council_url(council)
        driver.get(base_url)
        
        # Enter postcode
        try:
            input_field = wait.until(
                EC.presence_of_element_located((By.ID, "simpleSearchString"))
            )
            input_field.clear()
            input_field.send_keys(postcode)
            input_field.send_keys(Keys.RETURN)
        except Exception as e:
            print(f"Error finding postcode field: {e}")
            return []
        
        print(f"Searched for postcode: {postcode}")
        
        detail_urls = []
        
        # Collect URLs from all pages
        while True:
            random_sleep(2, 4)
            
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
                
                if "disabled" in next_button.get_attribute("class").lower():
                    break
                
                driver.execute_script("arguments[0].click();", next_button)
            except Exception:
                break
        
        return detail_urls
    
    finally:
        driver.quit()


def scrape_app_details(urls, os_type="mac", max_retries=3):
    """Scrape application details from URLs.
    
    Args:
        urls: List of application URLs
        os_type: "mac" or "linux"
        max_retries: Maximum retry attempts per URL
        
    Returns:
        Dictionary with scraped data
    """
    driver = setup_driver(os_type)
    wait = get_wait(driver)
    
    data = {
        "reference": [],
        "url": [],
        "date_validated": [],
        "address": [],
        "description": [],
        "decision": [],
        "decision_date": [],
        "app_type": [],
        "actual_decision_level": [],
        "expected_decision_level": []
    }
    
    try:
        for i, url in enumerate(urls, start=1):
            print(f"Scraping URL {i} of {len(urls)}: {url}")
            
            success = False
            
            for attempt in range(1, max_retries + 1):
                try:
                    print(f"  Attempt {attempt}/{max_retries}")
                    
                    # Scrape main page
                    driver.get(url)
                    
                    # Get reference
                    reference = get_table_value(driver, "Reference")
                    
                    if is_missing(reference):
                        raise ValueError("Reference missing")
                    
                    # Get all main details
                    date_validated = get_table_value(driver, "Application Validated")
                    address = get_table_value(driver, "Address")
                    description = get_table_value(driver, "Proposal")
                    decision = get_table_value(driver, "Decision")
                    decision_date = get_table_value(driver, "Decision Issued Date")
                    
                    print(f"  Scraped main page for {reference}")
                    
                    random_sleep(1.5, 5.0)
                    
                    # Scrape further info page
                    try:
                        further_url = url.replace("summary", "details")
                        driver.get(further_url)
                        random_sleep(1, 3)
                        
                        app_type = get_table_value(driver, "Application Type")
                        actual_level = get_table_value(driver, "Actual Decision Level")
                        expected_level = get_table_value(driver, "Expected Decision Level")
                        
                        print(f"  Scraped further info page for {reference}")
                    except Exception as e:
                        print(f"  Further info failed: {e}")
                        app_type = np.nan
                        actual_level = np.nan
                        expected_level = np.nan
                    
                    # Store data
                    data["reference"].append(reference)
                    data["url"].append(url)
                    data["date_validated"].append(date_validated)
                    data["address"].append(address)
                    data["description"].append(description)
                    data["decision"].append(decision)
                    data["decision_date"].append(decision_date)
                    data["app_type"].append(app_type)
                    data["actual_decision_level"].append(actual_level)
                    data["expected_decision_level"].append(expected_level)
                    
                    success = True
                    break
                
                except Exception as e:
                    print(f"  Attempt {attempt} failed: {e}")
                    random_sleep(60, 120)
            
            # If all attempts failed, append NaNs
            if not success:
                print(f"  All retries failed for {url}")
                data["reference"].append(np.nan)
                data["url"].append(url)
                data["date_validated"].append(np.nan)
                data["address"].append(np.nan)
                data["description"].append(np.nan)
                data["decision"].append(np.nan)
                data["decision_date"].append(np.nan)
                data["app_type"].append(np.nan)
                data["actual_decision_level"].append(np.nan)
                data["expected_decision_level"].append(np.nan)
            
            random_sleep(2, 8)
    
    finally:
        driver.quit()
    
    return data


def scrape_comments(driver, council, app_id, application_url, comments_saver=None):
    """Scrape comments from an application.
    
    Args:
        driver: Active WebDriver instance
        council: Council name
        app_id: Application ID
        application_url: Base URL of application
        comments_saver: Optional object with insert_comment() method
        
    Returns:
        Number of comments scraped
    """
    wait = get_wait(driver)
    comment_url = application_url.replace("summary", "neighbourComments")
    
    page_number = 1
    number_comments = 0
    seen_comments = set()
    
    while True:
        url = f"{comment_url}&neighbourCommentsPager.page={page_number}"
        
        try:
            driver.get(url)
        except WebDriverException as e:
            if '429' in str(e):
                print(f"429 Too Many Requests on page {page_number}. Sleeping 5 min.")
                time.sleep(300)
                continue
            else:
                print(f"WebDriverException on page {page_number}: {e}")
                return number_comments
        
        try:
            comments = wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'comment'))
            )
        except TimeoutException:
            print(f"No comments on page {page_number}")
            break
        
        has_new_comments = False
        
        for comment in comments:
            try:
                comment_text = comment.find_element(By.CLASS_NAME, 'comment-text').text.strip()
            except:
                comment_text = "None"
            
            # Check for duplicates
            comment_hash = hash((app_id, comment_text))
            if comment_hash in seen_comments:
                continue
            
            seen_comments.add(comment_hash)
            has_new_comments = True
            
            comment_id = f"{app_id}_{number_comments + 1}"
            
            try:
                address = comment.find_element(By.CLASS_NAME, 'consultationAddress').text.strip()
            except:
                address = "None"
            
            try:
                stance = comment.find_element(By.CLASS_NAME, 'consultationStance').text.strip().strip("()")
            except:
                stance = "None"
            
            try:
                date = comment.find_element(
                    By.XPATH,
                    './/h3[contains(text(), "Comment submitted date:")]'
                ).text.replace("Comment submitted date:", "").strip()
            except:
                date = "None"
            
            if comments_saver:
                comments_saver.insert_comment(
                    council, comment_id, app_id,
                    address, stance, date, comment_text
                )
            
            number_comments += 1
            random_sleep(1, 2)
        
        if not has_new_comments:
            print(f"No new comments on page {page_number}")
            break
        
        page_number += 1
        random_sleep(5, 10)
    
    return number_comments
