import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
from multiprocessing import Pool

def scrape_page(page_number):
    # Initialize your webdriver
    driver = webdriver.Chrome()  # Replace with your preferred webdriver

    # URL for the given page number
    url = f"https://www.naukri.com/data-analyst-jobs-{page_number}"
    driver.get(url)

    # Set a maximum time (in seconds) to wait for elements to be present
    wait = WebDriverWait(driver, 10)

    try:
        # Waiting (max 10 sec) for at least one element with the specified CSS selector
        job_tuples = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'srp-jobtuple-wrapper')))
    except TimeoutException:
        # If TimeoutException, refresh the page and try again
        driver.refresh()

    # Initialize an empty list to store data
    data_list = []

    # Get data from all received web elements
    for job_tuple in job_tuples:
        role = job_tuple.find_element(By.CLASS_NAME, 'row1').find_element(By.CLASS_NAME, 'title').text.strip()
        company_name = job_tuple.find_element(By.CLASS_NAME, 'row2').find_element(By.CLASS_NAME, 'comp-dtls-wrap').text.strip()
        experience = job_tuple.find_element(By.CLASS_NAME, 'row3').find_element(By.CLASS_NAME, 'ni-job-tuple-icon-srp-experience').text.strip()
        salary = job_tuple.find_element(By.CLASS_NAME, 'row3').find_element(By.CLASS_NAME, 'ni-job-tuple-icon-srp-rupee').text.strip()
        location = job_tuple.find_element(By.CLASS_NAME, 'row3').find_element(By.CLASS_NAME, 'ni-job-tuple-icon-srp-location').text.strip()

        # Extracting skills from row5 class
        skills_elements = job_tuple.find_element(By.CLASS_NAME, 'row5').find_elements(By.CLASS_NAME, 'tag-li')
        skills = [skill.text.strip() for skill in skills_elements]

        # Append data to the list
        data_list.append([role, company_name, experience, salary, location, ', '.join(skills)])

    # Close the webdriver
    driver.quit()

    # Return the data list
    return data_list

jobs_csv = r'c:\Users\Yash\Desktop\jobs.csv'

if __name__ == "__main__":
    # Initialize an empty list to store all data
    all_data = []

    # Scrape data from pages 1 to 5
    for page_number in range(1, 6):
        data_from_page = scrape_page(page_number)
        all_data.extend(data_from_page)

    # Create a DataFrame from the combined data
    columns = ['Role', 'Company Name', 'Experience', 'Salary', 'Location', 'Skills']
    df = pd.DataFrame(all_data, columns=columns)

    # Save the DataFrame to a CSV file
    df.to_csv(jobs_csv, index=False)