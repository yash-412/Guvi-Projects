import streamlit as st
import cv2
import numpy as np
import easyocr
import pandas as pd
from PIL import Image
from spellchecker import SpellChecker
import re
from sqlalchemy import create_engine, Column, Integer, String, Text, MetaData, Table
from sqlalchemy.orm import sessionmaker
import pymysql

db_user = 'root'
db_password = '+91naveen'
db_host = 'localhost'
db_port = 3306  # your database port
db_name = 'business cards'

engine = create_engine(f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

Session = sessionmaker(bind=engine)
session = Session()

metadata = MetaData()

business_cards = Table(
    'business_cards',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(255)),
    Column('designation', String(255)),
    Column('mobile', Text),
    Column('email', String(255)),
    Column('website', String(255)),
    Column('company', String(255)),
    Column('address', String(255))
)

metadata.create_all(engine)

def clean_text(image, left_region, right_region):
    result = reader.readtext(image)
    left_result = reader.readtext(left_region)
    right_result = reader.readtext(right_region)

    full_text = extract_text(result)
    left_text = extract_text(left_result)
    right_text = extract_text(right_result)

    return result, left_result, right_result, left_text, right_text

def spell_check(text, exceptions=[]):
    # Spell correction
    spell = SpellChecker()
    
    # Add exceptions to the known words
    for word in exceptions:
        spell.known([word])
    
    words = text.split()
    corrected_words = [spell.correction(word) for word in words]
    corrected_text = ' '.join(corrected_words)
    
    # Remove trailing white spaces
    corrected_text = re.sub(r'\s+$', '', corrected_text)
    
    return corrected_text

def extract_text(result):
    text_ = ""

    for detection in result:
        (text_bbox, text, prob) = detection
        text_ += text + " "
    return text_

def extract_text_lines(list_of_lists):
    # Initialize an empty list to store extracted text line by line
    extracted_text_lines = []

    # Iterate through the list of lists
    for sublist in list_of_lists:
        # Extract the text from each sublist (assuming text is the second element)
        text = sublist[1]

        # Append the extracted text to the result list
        extracted_text_lines.append(text)

    return extracted_text_lines

def extract_info(text):
    info = {
        "name": name,
        "designation": designation,
        "mobile": [],
        "email": "",
        "website": "",
        "company": company,
        "address": ""
    }

    # Define regular expressions for each type of information
    mobile_pattern = r'(?:\+\d{1,4}-\d{1,4}-\d{1,10}|\d{1,4}-\d{1,4}-\d{1,10})'
    email_pattern = r'[A-Za-z0-9_.]+@[A-Za-z0-9.-]+'
    website_pattern = r'[Ww][Ww][Ww](.*?)com'
    address_pattern = r'.*'  # Match anything for the address

    # Extract mobile numbers (multiple)
    mobile_matches = re.findall(mobile_pattern, text)
    info["mobile"].extend(mobile_matches)
    text = re.sub(mobile_pattern, "", text).strip()

    # Extract email
    email_match = re.search(email_pattern, text)
    if email_match:
        info["email"] = email_match.group()
        text = text.replace(info["email"], "").strip()

    # Extract website
    website_match = re.search(website_pattern, text)
    if website_match:
        info["website"] = website_match.group()
        text = text.replace(info["website"], "").strip()

    text = text.replace(info["name"], "").strip()
    text = text.replace(info["designation"], "").strip()
    text = text.replace(info["company"], "").strip()

    # The remaining text is considered the address
    info["address"] = text.strip()

    return info

exceptions = ['BORCELLE','borcelle']

reader = easyocr.Reader(['en'])

image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

image = Image.open(image)

image = np.array(image)

scale_factor = 1  # You can adjust this value as needed
image = cv2.resize(image, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)

thresholded_image = cv2.addWeighted(image, 2.3, np.zeros(image.shape, image.dtype), 0, 10)

thresholded_image = cv2.convertScaleAbs(thresholded_image, alpha=1.5, beta=50) 

# sharpening for better precision
sharpened_image = cv2.filter2D(image, -1, kernel=np.array([[-1, -1, -1],[-1,  9, -1],[-1, -1, -1]]))

# Convert the image to grayscale
gray_image = cv2.cvtColor(sharpened_image, cv2.COLOR_BGR2GRAY)

# Apply Gaussian blur to reduce noise
thresholded_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

# Apply adaptive thresholding for better contrast
# thresholded_image = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

split_x = thresholded_image.shape[1] // 2

# Define padding to be added to the right region (adjust as needed)
left_padding = 15
right_padding = 30

# Split the image into left and right regions with padding
left_region = image[:, :split_x - left_padding:] # new padding added
right_region = image[:, split_x - right_padding:]

result, left_result, right_result, left_text, right_text = clean_text(thresholded_image, left_region, right_region)

# left side has company name
# other details on right side
if len(left_result) < len(right_result):  
    info_result = right_result
else:
    info_result = left_result

if len(left_text) < len(right_text):
    company = left_text  
    info_text = right_text
else:
    company = right_text 
    info_text = left_text

new_info_text = extract_text_lines(info_result)

st.image(image, caption = "Uploaded Image", use_column_width=True)

name = new_info_text[0]
designation = new_info_text[1]
name, designation, company

x = extract_info(info_text)

corrected_website = x['website'].lower()
corrected_email = x['email'].lower()
x['address'] = re.sub(r'\bSt\b|,,|;', lambda match: 'st.' if match.group() == 'St' else ',', x['address'])
corrected_company = re.sub(r' " ' , '', x['company'])
corrected_website = re.sub(r'\s', '.', x['website'])

x['website'] = corrected_website
x['email'] = corrected_email
x['company'] = corrected_company.upper()
x['website'] = corrected_website.lower()
x['mobile'] = ', '.join(x['mobile'])
# x['company'] = spell_check(x['company'], exceptions)

if not re.search(r'\.com', x['website']):
    x['website'] = re.sub(r'(www\..*?)(com)', r'\1.\2', x['website'])

df = pd.DataFrame([x])

table_name = 'business card'

st.write(df)

if st.button("Insert Data into Database"):
    # Insert the data into the table
    insert_statement = business_cards.insert().values(**x)
    session.execute(insert_statement)
    st.success("Data Inserted Data into Database")
session.commit()

session.close()

# streamlit run C:\Users\Yash\test_image_extract.py