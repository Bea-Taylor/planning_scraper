import pandas as pd
import time
import random
import os
import re
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

import sys
sys.path.append('../pipeline')
from comments_saver import CommentsSaver
cs = CommentsSaver()

class CouncilScraper:

    def __init__(self):
        pass

    def council_web_address(council):
        """Returns URL for council planning application page.

        Args:
            council (string): London borough council name

        Returns:
            string: URL for council planning application page
        """

        council = council.lower().strip()
        url_df = pd.read_csv("../data/example_urls.csv")
        return url_df[url_df["council"] == council]["url"].values[0]
        
        # if council == "newham":
        #     return "https://pa.newham.gov.uk/online-applications"
        # elif council == "southwark":
        #     return "https://planning.southwark.gov.uk/online-applications"
        # elif council == "lambeth":
        #     return "https://planning.lambeth.gov.uk/online-applications"
        # elif council == "ealing":
        #     return "https://pam.ealing.gov.uk/online-applications"
        # elif council == "city of london":
        #     return "https://www.planning2.cityoflondon.gov.uk/online-applications"
        # elif council == "bromley":
        #     return "https://searchapplications.bromley.gov.uk/online-applications"
        # elif council == "brent":
        #     return "https://pa.brent.gov.uk/online-applications"
        # elif council == "barnet":
        #     return "https://publicaccess.barnet.gov.uk/online-applications"
        # elif council == 'westminster':
        #     return "https://idoxpa.westminster.gov.uk/online-applications"
        
    
    def driver_options(os="mac"):
        """Returns the service and options for Selenium WebDriver.

        Returns:
            tuple: service and options for Selenium WebDriver
        """
        if os=="mac":
            options = Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--headless")
            options.add_argument('--disable-images')  # Disable images
            options.add_argument('--disable-plugins')  # Disable plugins like Flash
            options.add_argument("--disable-javascript")  # Disable JS execution if possible
            service = webdriver.ChromeService()

            return service, options

        elif os=="linux":
            # Establish options for Selenium WebDriver
            CHROMEDRIVER_PATH = "/usr/bin/chromedriver"
            CHROME_BINARY_PATH = "/usr/bin/chromium"

            options = webdriver.ChromeOptions()
            options.binary_location = CHROME_BINARY_PATH  # Set Chromium as the browser
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--headless=new")  # Run Chrome in headless mode
            options.add_argument("--remote-debugging-port=9230")  # Avoid conflicts with other Chrome instances
            options.add_argument('--disable-images')  # Disable images
            options.add_argument('--disable-plugins')  # Disable plugins like Flash
            options.add_argument("--disable-javascript")  # Disable JS execution if possible
            service = Service(CHROMEDRIVER_PATH)  # Explicitly define the path to chromedriver
            
            return service, options


    def get_application_page(driver, council, app_id):
        """Returns the URL of the planning application page for a given council and application ID (lpa_app_no).

        Args:
            council (string): London borough council name
            app_id (string): planning application ID

        Returns:
            string: URL of the planning application page
        """

        wait = WebDriverWait(driver, 10)

        base_url = CouncilScraper.council_web_address(council=council)
        url = base_url + "/search.do?action=advanced"

        driver.get(url)

        # Locate the input field by its ID
        try:
            input_field = wait.until(EC.presence_of_element_located((By.ID, "reference")))
            # Clear any existing text and enter the application reference code
            input_field.clear()
            input_field.send_keys(app_id)
        except Exception as e:
            print(f"Error finding reference field: {e}")
            driver.quit()
            return "Address not found"

        # Press Enter to submit
        input_field.send_keys(Keys.RETURN)
        print(f"Searched for application ID: {app_id}.")
        time.sleep(random.uniform(4, 10))

        # Click on the "Details" tab
        try:
            details_tab = wait.until(EC.element_to_be_clickable((By.ID, "tab_summary")))
            details_tab.click()
        except Exception as e:
            print(f"Error clicking on 'Details' tab: {e}")
            driver.quit()
            return "Address not found"

        application_url = driver.current_url
        print("Found URL address")
        time.sleep(random.uniform(2, 5))

        return application_url
    

    def get_postcode_page(driver, council, postcode):
        """Returns the URL of the planning application page for a given council and postcode.

        Args:
            council (string): London borough council name
            postcode (string): postcode

        Returns:
            string: URL of the planning application page
        """

        wait = WebDriverWait(driver, 10)

        url = CouncilScraper.council_web_address(council=council)
        # url = base_url + "/search.do?action=advanced"

        driver.get(url)

        # Locate the input field by its ID
        try:
            input_field = wait.until(EC.presence_of_element_located((By.ID, "simpleSearchString")))
            # Clear any existing text and enter the application reference code
            input_field.clear()
            input_field.send_keys(postcode)
        except Exception as e:
            print(f"Error finding matching postcode: {e}")
            driver.quit()
            return "No applications at postcode found"

        # Press Enter to submit
        input_field.send_keys(Keys.RETURN)
        print(f"Searched for postcode: {postcode}.")
        time.sleep(random.uniform(4, 10))

        # # Click on the "Details" tab
        # try:
        #     details_tab = wait.until(EC.element_to_be_clickable((By.ID, "tab_summary")))
        #     details_tab.click()
        # except Exception as e:
        #     print(f"Error clicking on 'Details' tab: {e}")
        #     driver.quit()
        #     return "Address not found"

        postcode_url = driver.current_url
        print("Found URL address")
        time.sleep(random.uniform(2, 5))

        return postcode_url


    def has_comments(driver, url):
        """Checks if a given web address has comments.

        Args:
            url (string): web adress to check

        Returns:
            bool: returns True if comments are found, False otherwise
        """

        wait = WebDriverWait(driver, 10) 

        try:
            # Open the URL
            driver.get(url)

            # Find the "Comments Received" element
            comment_element = wait.until(EC.element_to_be_clickable((By.ID, "tab_makeComment")))
            
            if comment_element:
                comment_text = comment_element.text

                # Extract number inside parentheses using regex
                match = re.search(r"\((\d+)\)", comment_text)
                if match:
                    comments_count = int(match.group(1))
                    return comments_count > 0

        except Exception as e:
            print(f"Error: {e}")
        
        return False  # Return False if the element is not found



    # def scrape_comments_remote(driver, council, app_id, application_url):
    #     """Scrapes comments from a given planning application page."""

    #     wait = WebDriverWait(driver, 10)
    #     comment_url = application_url.replace("summary", "neighbourComments")

    #     page_number = 1
    #     number_comments = 0
    #     max_retries = 1
    #     retry_count = 0

    #     while True:
    #         url = f"{comment_url}&neighbourCommentsPager.page={page_number}"
            
    #         try:
    #             driver.get(url)
    #         except WebDriverException as e:
    #             if '429' in str(e):
    #                 print(f"429 Too Many Requests error on page {page_number}. Sleeping for 5 minutes.")
    #                 time.sleep(300)
    #                 continue  
    #             else:
    #                 print(f"WebDriverException on page {page_number}: {e}")
    #                 return number_comments # stop scraping

    #         try:
    #             comments = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'comment')))
    #         except TimeoutException:
    #             print(f"Timeout: No comments found on page {page_number}. Retrying...")
    #             retry_count += 1
    #             if retry_count >= max_retries:
    #                 print(f"Max retries reached. Stopping scraping.")
    #                 return  number_comments 
    #             time.sleep(random.uniform(60, 120))
    #             continue  

    #         retry_count = 0  

    #         for comment in comments:
    #             comment_id = app_id + "_" + str(number_comments + 1)
    #             try:
    #                 address = comment.find_element(By.CLASS_NAME, 'consultationAddress').text.strip()
    #             except:
    #                 address = "None"

    #             try:
    #                 stance = comment.find_element(By.CLASS_NAME, 'consultationStance').text.strip().strip("()")
    #             except:
    #                 stance = "None"

    #             try:
    #                 date = comment.find_element(By.XPATH, './/h3[contains(text(), "Comment submitted date:")]').text.replace("Comment submitted date:", "").strip()
    #             except:
    #                 date = "None"

    #             try:
    #                 comment_text = comment.find_element(By.CLASS_NAME, 'comment-text').text.strip()
    #             except:
    #                 comment_text = "None"

    #             cs.insert_comment(council, comment_id, app_id, address, stance, date, comment_text)
    #             number_comments += 1

    #             time.sleep(random.uniform(1, 2))  

    #         page_number += 1
    #         time.sleep(random.uniform(5, 10))  

    #     # print(f'Finished scraping. Pages: {page_number}, Comments: {number_comments}')
    #     # return 


    def scrape_comments_remote(driver, council, app_id, application_url):
        """Scrapes comments from a given planning application page, avoiding duplicates."""

        wait = WebDriverWait(driver, 10)
        comment_url = application_url.replace("summary", "neighbourComments")

        page_number = 1
        number_comments = 0
        max_retries = 1
        retry_count = 0

        seen_comments = set()  # Track already seen comments to prevent duplicates

        while True:
            url = f"{comment_url}&neighbourCommentsPager.page={page_number}"
                
            try:
                driver.get(url)
            except WebDriverException as e:
                if '429' in str(e):
                    print(f"429 Too Many Requests error on page {page_number}. Sleeping for 5 minutes.")
                    time.sleep(300)
                    continue  
                else:
                    print(f"WebDriverException on page {page_number}: {e}")
                    return number_comments  # Stop scraping

            try:
                comments = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'comment')))
            except TimeoutException:
                print(f"Timeout: No comments found on page {page_number}. Retrying...")
                retry_count += 1
                if retry_count >= max_retries:
                    print(f"Max retries reached. Stopping scraping.")
                    return number_comments
                time.sleep(random.uniform(60, 120))
                continue  

            retry_count = 0  

            has_new_comments = False  # Track if this page has new comments

            for comment in comments:
                try:
                    comment_text = comment.find_element(By.CLASS_NAME, 'comment-text').text.strip()
                except:
                    comment_text = "None"

                # Create a unique hash for each comment based on its content
                comment_hash = hash((app_id, comment_text))

                if comment_hash in seen_comments:
                    print(f"Duplicate comment detected on page {page_number}, skipping...")
                    continue  # Skip duplicate comment

                seen_comments.add(comment_hash)  # Store the comment hash
                has_new_comments = True  # Mark that new comments were found
                    
                comment_id = app_id + "_" + str(number_comments + 1)
                    
                try:
                    address = comment.find_element(By.CLASS_NAME, 'consultationAddress').text.strip()
                except:
                    address = "None"

                try:
                    stance = comment.find_element(By.CLASS_NAME, 'consultationStance').text.strip().strip("()")
                except:
                    stance = "None"

                try:
                    date = comment.find_element(By.XPATH, './/h3[contains(text(), "Comment submitted date:")]').text.replace("Comment submitted date:", "").strip()
                except:
                    date = "None"

                cs.insert_comment(council, comment_id, app_id, address, stance, date, comment_text)
                number_comments += 1

                time.sleep(random.uniform(1, 2))  

            if not has_new_comments:
                print(f"No new comments found on page {page_number}. Stopping pagination.")
                break  # Stop pagination if no new comments appear

            page_number += 1
            time.sleep(random.uniform(5, 10))  

        return number_comments



    def get_application_comments(os, council, app_id):

        # Set up Selenium WebDriver
        service, options = CouncilScraper.driver_options(os)
        driver = webdriver.Chrome(service=service, options=options)

        # Get the application page URL
        application_url = CouncilScraper.get_application_page(driver, council, app_id)  

        if CouncilScraper.has_comments(driver, application_url):
            print("Comments found for the given application.")
            number_comments = CouncilScraper.scrape_comments_remote(driver, council, app_id, application_url)

            driver.stop_client()
            driver.close()
            driver.quit()
            return number_comments
        
        else:
            print("No comments found for the given application.")
            driver.stop_client()
            driver.close()
            driver.quit()
            return 0