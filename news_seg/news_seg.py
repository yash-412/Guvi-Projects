# Article seggregation
nltk.download('stopwords')
nltk.download('punkt')

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

punctuations = list(string.punctuation)

# # Now you can import the NLTK resources as usual
from nltk.corpus import wordnet

# nltk.download('wordnet')
# from nltk.corpus import wordnet
lemmatizer = WordNetLemmatizer()
stopwords = set(stopwords.words('english'))
# nltk.data.path.append('./kaggle/input/')

news_df = pd.read_json('/content/News_Category_Dataset_v3.json', lines=True)

df = news_df[['headline','category']]
from sklearn.feature_extraction.text import CountVectorizer

x = np.array(df['headline'])
y = np.array(df['category'])

m = CountVectorizer()
x = m.fit_transform(x)

from sklearn.model_selection import train_test_split
xtrain,xtest,ytrain,ytest =train_test_split(x,y,test_size = 0.20)

from sklearn.naive_bayes import MultinomialNB

model = MultinomialNB()
model.fit(xtrain,ytrain)

input = input()
text = m.transform([input]).toarray()

model.predict(text)

def scrape_and_analyze(url):
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

scrape_and_analyze('https://www.bbc.com/news/world-67858016')