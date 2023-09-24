# pdf miner and open api integration part

import os
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from pdfminer.high_level import extract_text
import openai

# Set your OpenAI API key here
api_key = ""
openai.api_key = api_key

def on_drop(event):
    file_path = event.data
    process_pdf(file_path)

def process_pdf(pdf_file_path):
    # Extract text from the PDF file using pdfminer
    pdf_text = extract_text(pdf_file_path)

    # Analyze the PDF text using ChatGPT
    analysis = analyze_text(pdf_text)

    # Print the analysis results
    print(analysis)
# ALTER THE PROMPT BEFOREHAND AND DO NOT RUN TILL CONFIRMED
def analyze_text(text):
    # Call the ChatGPT API to analyze the text
    response = openai.Completion.create(
        engine="davinci",
        prompt=f"Analyze this resume text and give in a maximum of 3 words which job this resume is suitable for by cross checking with jobs in linkedIn:\n{text}\n\nAnalysis:",
        max_tokens=200  # Adjust the number of tokens as needed
    )

    # Extract the generated analysis from the API response
    analysis = response.choices[0].text

    return analysis

# Create a root window for the GUI
root = TkinterDnD.Tk()
root.title("PDF File Drag and Drop")

# Create a label for instructions
instructions_label = tk.Label(root, text="Drag and drop a PDF file here")
instructions_label.pack(pady=20)

# Create a drop target
drop_target = tk.Label(root, text="Drop Here", bg="lightgray", width=40, height=10)
drop_target.pack()

# Bind the drop event to the on_drop function
drop_target.drop_target_register(DND_FILES)
drop_target.dnd_bind('<<Drop>>', on_drop)

# Start the GUI main loop
root.mainloop()

# job description extraction part 

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Prompt the user for a job title
job_title = input("Enter a job title: ")
location = input("Enter a location: ")
# Set up the WebDriver with the path to your Chrome WebDriver executable
driver = webdriver.Edge()

# URL of the Indeed website
url = 'https://in.indeed.com/'

# Open the URL in the browser
driver.get(url)

# Wait for the search bar to become clickable
search_bar = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//*[@id="text-input-what"]'))
)

# Enter the job title in the search bar
search_bar.send_keys(job_title)

# Wait for the location search bar to become clickable
location_search_bar = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//*[@id="text-input-where"]'))
)

# Enter the location in the location search bar
location_search_bar.send_keys(location)

# Simulate pressing Enter to submit the search
location_search_bar.send_keys(Keys.RETURN)

# Close the browser window after a few seconds (you can adjust the delay)
#driver.implicitly_wait(30)

time.sleep(3)

# Quit the WebDriver
driver.quit()