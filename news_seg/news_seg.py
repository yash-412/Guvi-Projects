# nltk.download('stopwords')
# nltk.download('punkt')

import streamlit as st
import pandas as pd
import numpy as np
import nltk
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize, pos_tag
import subprocess
import shutil
import string
from bs4 import BeautifulSoup
import requests
from nltk.corpus import wordnet
import joblib
from transformers import BartForConditionalGeneration, BartTokenizer
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import LinearSVC

# Load pre-trained model and tokenizer
model_name = "facebook/bart-large-cnn"
model = BartForConditionalGeneration.from_pretrained(model_name)
tokenizer = BartTokenizer.from_pretrained(model_name)

punctuations = list(string.punctuation)
lemmatizer = WordNetLemmatizer()
stopwords = set(stopwords.words('english'))

def scrape(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract the article title
    title_element = soup.find("h1")
    title = title_element.text.strip() if title_element else ""

    # Extract the article text
    article_text = ""
    article_elements = soup.find_all("p")
    for element in article_elements:
        if "entry-title" in element.get("class", []):
            continue
        if "tdm-descr" in element.get("class", []):
            continue
        article_text += element.text.strip() + " "

    return title, article_text

# nom_model = joblib.load(r'd:\VSCodium\Guvi-Projects\news_seg\model.joblib')

with open(r'd:\VSCodium\Guvi-Projects\news_seg\best_model.pkl', 'rb') as file:
    saved_data = pickle.load(file)

nom_model = saved_data['model']
m = saved_data['vectorizer']

st.title("News Summary and Classification App")

# Input URL
url = st.text_input("Enter the URL of the news article:")

# Scrape and summarize the article
if st.button("Enter"):
    title, article_text = scrape(url)
    inputs = tokenizer(article_text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(inputs["input_ids"], max_length=150, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    st.subheader("Article Title:")
    st.write(title)

    st.subheader("Summary:")
    st.write(summary)

    st.markdown(f"[Open Website]( {url})", unsafe_allow_html=True)

    # Predict category using the classification model
    text = m.transform([summary]).toarray()
    result = nom_model.predict(text)
    st.subheader("Predicted Category:")
    st.markdown(f"<p style='font-size: 20px; text-align: center;'> {result[0]}</p>", unsafe_allow_html=True)

# streamlit run D:\VSCodium\Guvi-Projects\news_seg\news_seg.py