import streamlit as st
import cv2
import numpy as np
from PIL import Image
import easyocr
import re

# Initialize EasyOCR
reader = easyocr.Reader(['en'])

# Function to apply image processing based on user input
def process_image(image, sharpness, brightness, contrast, threshold):
    # Convert PIL image to OpenCV format
    image = np.array(image)
    
    # Apply sharpening
    kernel = np.array([[-1, -1, -1], [-1, sharpness, -1], [-1, -1, -1]])
    sharpened_image = cv2.filter2D(image, -1, kernel)
    
    # Adjust brightness and contrast
    enhanced_image = cv2.convertScaleAbs(sharpened_image, alpha=contrast, beta=brightness)
    
    # Convert the image to grayscale
    gray_image = cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    
    # Apply adaptive thresholding
    thresholded_image = cv2.adaptiveThreshold(blurred_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, threshold)
    
    return thresholded_image

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
    website_pattern = r'[Ww][Ww][Ww](.*?)\.com'
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

def extract_text(result):
    text_ = ""

    for detection in result:
        (text_bbox, text, prob) = detection
        text_ += text + " "
    return text_

def clean_text(image, left_region, right_region):
    result = reader.readtext(image)
    left_result = reader.readtext(left_region)
    right_result = reader.readtext(right_region)

    full_text = extract_text(result)
    left_text = extract_text(left_result)
    right_text = extract_text(right_result)

    return result, left_result, right_result, left_text, right_text

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
    website_pattern = r'[Ww][Ww][Ww](.*?)\.com'
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

def split_image(processed_image):
    split_x = processed_image.shape[1] // 2

    # Define padding to be added to the right region (adjust as needed)
    left_padding = 40
    right_padding = 40

    # Split the image into left and right regions with padding
    left_region = processed_image[:, :split_x - left_padding:]
    right_region = processed_image[:, split_x - right_padding:]

    return left_region, right_region

# Streamlit app
st.title("Test Bixcard-X")

# Define columns for layout
left_column, right_column = st.columns(2)

# Upload an image
uploaded_image = left_column.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

pil_image = Image.open(uploaded_image)

reset_button = st.button("Reset")

# Default slider values
default_sharpness = 9.0
default_brightness = 1.0
default_contrast = 1.0
default_threshold = 2.0

if reset_button:

    # Reset sliders to default values
    sharpness = default_sharpness
    brightness = default_brightness
    contrast = default_contrast
    threshold = default_threshold

# Sliders for adjusting parameters for the selected region
sharpness = 9.0
brightness = 1.0
contrast = 1.0
threshold = 2.0

processed_image = process_image(pil_image, sharpness, brightness, contrast, threshold)

left_region, right_region = split_image(processed_image)

# Create select boxes for left and right regions
selected_region = st.selectbox("Select Region to Edit", ["Left Region", "Right Region"])

# Define the regions based on user selection
if selected_region == "Left Region":
    region = left_region
    column = left_column
else:
    region = right_region
    column = left_column

# Sliders for adjusting parameters for the selected region
sharpness = column.slider("Sharpness", 1.0, 20.0, default_sharpness, step=0.1)
brightness = column.slider("Brightness", -10.0, 10.0, default_brightness, step=0.1)
contrast = column.slider("Contrast", -10.0, 10.0, default_contrast, step=0.1)
threshold = column.slider("Threshold", -10.0, 10.0, default_threshold, step=2.0)

if uploaded_image is not None:

    # Read the uploaded image as a PIL image
    pil_image = Image.open(uploaded_image)

    # Apply image processing
    processed_image = process_image(pil_image, sharpness, brightness, contrast, threshold)
    
    split_x = processed_image.shape[1] // 2

    # Define padding to be added to the right region (adjust as needed)
    left_padding = 40
    right_padding = 40

    # Split the image into left and right regions with padding
    left_region = processed_image[:, :split_x - left_padding:]
    right_region = processed_image[:, split_x - right_padding:]

    left_column.image(pil_image, caption = "Original Image", use_column_width=True)

    # Display the original and processed images on the right column
    right_column.image([left_region, right_region], caption=["Left Region", "Right Region"], use_column_width=True)

    result, left_result, right_result, left_text, right_text = clean_text(processed_image, left_region, right_region)

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

    image_text_lines = extract_text_lines(info_result) # extract_text function is deemed unnecessary

    name = image_text_lines[0]
    designation = image_text_lines[1]

    image_text = extract_text(info_result)

    main_df = extract_info(image_text)
    
    st.write(main_df)

# streamlit run C:\Users\Yash\test_image_extract.py