"""Core scraping logic and orchestration."""

import time
import random
import numpy as np
from typing import List, Dict, Any, Optional

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .config import Config
from .browser import setup_driver, check_rate_limit
from .navigation import build_further_info_url, build_comments_url
from .parsers import parse_application_details, parse_further_info


class ApplicationScraper:
    """Main scraper class for planning applications."""
    
    def __init__(self, os_type: str = "mac", max_retries: int = None):
        """Initialize the scraper.
        
        Args:
            os_type: Operating system type ("mac" or "linux")
            max_retries: Maximum number of retries for failed requests
        """
        self.os_type = os_type
        self.max_retries = max_retries or Config.MAX_RETRIES
    
    def scrape_app_details(self, urls: List[str]) -> Dict[str, List[Any]]:
        """Scrape application details from a list of URLs.
        
        Args:
            urls: List of application page URLs
            
        Returns:
            Dictionary with keys for each data field and lists of values
        """
        driver = setup_driver(self.os_type)
        wait = WebDriverWait(driver, Config.DEFAULT_WAIT_TIMEOUT)
        
        data = {
            "reference": [],
            "url": [],
            "date_validated": [],
            "address": [],
            "description": [],
            "decision": [],
            "decision_date": [],
            "app type": [],
            "actual_decision_level": [],
            "expected_decision_level": []
        }
        
        try:
            for i, url in enumerate(urls, start=1):
                print(f"Scraping URL {i} of {len(urls)}: {url}")
                
                success = False
                
                for attempt in range(1, self.max_retries + 1):
                    try:
                        print(f"  Attempt {attempt}/{self.max_retries}")
                        
                        # Scrape main page
                        driver.get(url)
                        
                        # Wait for reference to ensure page loaded
                        reference = wait.until(
                            lambda d: parse_application_details(d)["reference"]
                        )
                        
                        if not reference or np.isnan(reference):
                            raise ValueError("Reference missing")
                        
                        # Parse main details
                        main_details = parse_application_details(driver)
                        print(f"  Scraped main page for {reference}")
                        
                        time.sleep(random.uniform(1.5, 5.0))
                        
                        # Scrape further info page
                        try:
                            driver.get(build_further_info_url(url))
                            time.sleep(random.uniform(1, 3))
                            
                            further_info = parse_further_info(driver)
                            print(f"  Scraped further info page for {reference}")
                        except Exception as e:
                            print(f"  Further info failed: {e}")
                            further_info = {
                                "app_type": np.nan,
                                "actual_decision_level": np.nan,
                                "expected_decision_level": np.nan
                            }
                        
                        # Store all data
                        data["reference"].append(main_details["reference"])
                        data["url"].append(url)
                        data["date_validated"].append(main_details["date_validated"])
                        data["address"].append(main_details["address"])
                        data["description"].append(main_details["description"])
                        data["decision"].append(main_details["decision"])
                        data["decision_date"].append(main_details["decision_date"])
                        data["app type"].append(further_info["app_type"])
                        data["actual_decision_level"].append(further_info["actual_decision_level"])
                        data["expected_decision_level"].append(further_info["expected_decision_level"])
                        
                        success = True
                        break
                    
                    except Exception as e:
                        print(f"  Attempt {attempt} failed: {e}")
                        time.sleep(random.uniform(
                            Config.RETRY_SLEEP_MIN,
                            Config.RETRY_SLEEP_MAX
                        ))
                
                # If all attempts failed, append NaNs
                if not success:
                    print(f"  All retries failed for {url}, recording NaNs")
                    data["reference"].append(np.nan)
                    data["url"].append(url)
                    data["date_validated"].append(np.nan)
                    data["address"].append(np.nan)
                    data["description"].append(np.nan)
                    data["decision"].append(np.nan)
                    data["decision_date"].append(np.nan)
                    data["app type"].append(np.nan)
                    data["actual_decision_level"].append(np.nan)
                    data["expected_decision_level"].append(np.nan)
                
                time.sleep(random.uniform(2, 8))
        
        finally:
            driver.quit()
        
        return data
    
    def scrape_comments(
        self,
        driver: webdriver.Chrome,
        council: str,
        app_id: str,
        application_url: str,
        comments_saver: Optional[Any] = None
    ) -> int:
        """Scrape comments from a planning application page.
        
        Args:
            driver: Active WebDriver instance
            council: Council name
            app_id: Application ID
            application_url: Base URL of the application
            comments_saver: Optional CommentsSaver instance for saving to database
            
        Returns:
            Total number of comments scraped
        """
        wait = WebDriverWait(driver, Config.DEFAULT_WAIT_TIMEOUT)
        
        page_number = 1
        number_comments = 0
        max_retries = 1
        retry_count = 0
        
        seen_comments = set()  # Track duplicates
        
        while True:
            url = build_comments_url(application_url, page_number)
            
            try:
                driver.get(url)
            except WebDriverException as e:
                if '429' in str(e):
                    print(f"429 Too Many Requests on page {page_number}. Sleeping 5 min.")
                    time.sleep(Config.RATE_LIMIT_SLEEP)
                    continue
                else:
                    print(f"WebDriverException on page {page_number}: {e}")
                    return number_comments
            
            try:
                comments = wait.until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'comment'))
                )
            except TimeoutException:
                print(f"Timeout: No comments on page {page_number}. Retrying...")
                retry_count += 1
                if retry_count >= max_retries:
                    print(f"Max retries reached. Stopping scraping.")
                    return number_comments
                time.sleep(random.uniform(60, 120))
                continue
            
            retry_count = 0
            has_new_comments = False
            
            for comment in comments:
                try:
                    comment_text = comment.find_element(
                        By.CLASS_NAME, 'comment-text'
                    ).text.strip()
                except:
                    comment_text = "None"
                
                # Check for duplicates
                comment_hash = hash((app_id, comment_text))
                if comment_hash in seen_comments:
                    print(f"Duplicate comment on page {page_number}, skipping...")
                    continue
                
                seen_comments.add(comment_hash)
                has_new_comments = True
                
                comment_id = f"{app_id}_{number_comments + 1}"
                
                # Extract comment details
                try:
                    address = comment.find_element(
                        By.CLASS_NAME, 'consultationAddress'
                    ).text.strip()
                except:
                    address = "None"
                
                try:
                    stance = comment.find_element(
                        By.CLASS_NAME, 'consultationStance'
                    ).text.strip().strip("()")
                except:
                    stance = "None"
                
                try:
                    date = comment.find_element(
                        By.XPATH,
                        './/h3[contains(text(), "Comment submitted date:")]'
                    ).text.replace("Comment submitted date:", "").strip()
                except:
                    date = "None"
                
                # Save comment if saver provided
                if comments_saver:
                    comments_saver.insert_comment(
                        council, comment_id, app_id,
                        address, stance, date, comment_text
                    )
                
                number_comments += 1
                time.sleep(random.uniform(1, 2))
            
            if not has_new_comments:
                print(f"No new comments on page {page_number}. Stopping.")
                break
            
            page_number += 1
            time.sleep(random.uniform(5, 10))
        
        return number_comments
