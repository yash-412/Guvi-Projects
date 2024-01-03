# nltk.download('stopwords')
# nltk.download('punkt')

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

model = joblib.load(r'd:\VSCodium\Guvi-Projects\news_seg\model.joblib')

url = input()
title, article_text = scrape(url)
text = m.transform([article_text]).toarray()

result = model.predict(text)

print(result)