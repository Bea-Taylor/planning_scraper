import time
import random
import json
import os 

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException


def council_web_address(council):
    council = council.lower().strip()
    if council == "newham":
        return "https://pa.newham.gov.uk/online-applications/applicationDetails.do?"
    elif council == 'westminster':
        return "https://idoxpa.westminster.gov.uk/online-applications/applicationDetails.do?"


def app_extractor(council, key_val):

    council = council.lower().strip()
    base_url = council_web_address(council) 

    driver = webdriver.Chrome() 
    home_url = base_url + "activeTab=summary&keyVal=" + key_val

    driver.get(home_url)

    # Wait for the comments section to load
    time.sleep(random.uniform(1, 5))  # Wait for the page to load
            
    # Find all div elements with the class "comment-text"
    ref_element = driver.find_elements(By.CLASS_NAME, 'caseNumber')
    ref = ref_element[0].text.strip()
    print(f'Application reference: {ref}')
    ref_num = ref.replace("/", "_")

    comment_url = base_url + "activeTab=neighbourComments&keyVal=" + key_val
    comments_path = "../outputs/" + council + "_" + ref_num + ".txt"

    page_number = 1
    number_comments = 0

    # Maximum number of retries for the same page
    max_retries = 1
    retry_count = 0

    # Ensure the directory exists
    os.makedirs(os.path.dirname(comments_path), exist_ok=True)

    if os.path.exists(comments_path):
        print(f"File already exists: {comments_path} \n Supply a new file path.")
        driver.quit()
        return
    else:
        while True:
            # Construct the full URL with the current page number
            url = f"{comment_url}&neighbourCommentsPager.page={page_number}"

            try:
                driver.get(url)
            except WebDriverException as e:
                if '429' in str(e):
                    print(f"Encountered 429 Too Many Requests error on page {page_number}. Sleeping for 5 minutes.")
                    time.sleep(300)  # Sleep for 5 minutes
                    continue  # Retry the request after sleeping

            # Wait for the comments section to load
            # WebDriverWait(driver, 10).until(
            # EC.presence_of_all_elements_located((By.CLASS_NAME, 'comment-text'))
            # )

            time.sleep(random.uniform(1, 5))  # Wait for the page to load
            

            # Find all comments on the page
            comments = driver.find_elements(By.CLASS_NAME, 'comment')

            if not comments:
                retry_count += 1
                if retry_count >= max_retries:
                    print(f"No more comments found after {max_retries} retries on page {page_number}.")
                    break  # Exit the loop if max retries are reached
                else:
                    print(f"No comments found on page {page_number}, retrying... ({retry_count}/{max_retries})")
                    time.sleep(random.uniform(280, 320))  # Sleep before retrying to avoid rapid re-requests
                    continue  # Retry the current page
            
            # Reset retry count after successful load
            retry_count = 0

            # Initialize lists to store the extracted data
            all_comments = []

            for comment in comments:
                try:
                    # Extract the address
                    address_element = comment.find_element(By.CLASS_NAME, 'consultationAddress')
                    address = address_element.text.strip()
                except:
                    address = "None"

                try:
                    # Extract the stance
                    stance_element = comment.find_element(By.CLASS_NAME, 'consultationStance')
                    stance = stance_element.text.strip().strip("()")  # Remove surrounding parentheses
                except:
                    stance = "None"

                try:
                    # Extract the submission date
                    date_element = comment.find_element(By.XPATH, './/h3[contains(text(), "Comment submitted date:")]')
                    date = date_element.text.replace("Comment submitted date:", "").strip()
                except:
                    date = "None"

                try:
                    # Extract the comment text
                    comment_text_element = comment.find_element(By.CLASS_NAME, 'comment-text')
                    comment_text = comment_text_element.text.strip()
                except:
                    comment_text = "None"

                # Append the extracted data as a dictionary
                all_comments.append({
                    "address": address,
                    "stance": stance,
                    "date": date,
                    "comment_text": comment_text
                })

            # # Find all div elements with the class "comment-text"
            # comments = driver.find_elements(By.CLASS_NAME, 'comment-text')
            
            with open(comments_path, "a") as file:
                for comment in all_comments:
                    file.write(json.dumps(comment))
                    file.write("\n")
                    number_comments += 1
                # comments_list.append(comment.text.strip())
            
            # Move to the next page
            page_number += 1
            
            # Introduce a random delay between 1 and 5 seconds
            time.sleep(random.uniform(1, 20)) # make this more random to avoid detection

    print(f'Page number reached: {page_number}')
    print(f'Number of comments: {number_comments}')
    print(f'Comments saved to: {comments_path}')

    # Quit the driver
    driver.quit()
    return 