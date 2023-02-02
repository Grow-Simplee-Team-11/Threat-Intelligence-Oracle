from pprint import pprint
from transformers import AutoModelForSequenceClassification
from transformers import TFAutoModelForSequenceClassification
from transformers import AutoTokenizer, AutoConfig
from transformers import pipeline

from scipy.special import softmax

import numpy as np
import nltk
import nltk.data
from nltk.stem.porter import *
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords

nltk.download('omw-1.4')
nltk.download('wordnet')
nltk.download('stopwords')

# english Stopwords
stop = set(stopwords.words("english"))

# Porter Stemmer
ps = PorterStemmer()

# Wordnet Lemmatizer
lmtzr = WordNetLemmatizer()

# Task to perform (sentiment or emotion) - change this to 'emotion' to perform emotion analysis instead
task = 'sentiment'

# Load the model and tokenizer for the task specified above (sentiment or emotion)
MODEL = f"cardiffnlp/twitter-roberta-base-{task}-latest"

tokenizer = AutoTokenizer.from_pretrained(
    MODEL, use_fast=True, padding=True, truncation=True)
config = AutoConfig.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)


def clean_text(text, deep=False):
    """
    Clean the text of the tweet
    :param text: text of the tweet
    :param deep: deep cleaning
    :return: cleaned text
    """

    # Step 1: Remove usernames tagged in the tweet
    text = ' '.join([word for word in text.split()
                    if not word.startswith('@')])

    # Step 2: Remove the URLs from the text
    text = ' '.join([word for word in text.split()
                    if not word.startswith('http')])

    if deep == True:
        # Step 3: Remove stopwords from text
        text = ' '.join([word for word in text.split() if word not in stop])

        # Step 4: Replace special characters. Only keed alphanumeric characters
        text = re.sub('[^a-zA-Z0-9]+', ' ', text)

        # Step 5: Stem the words to extract the root of each word[]
        text = ' '.join([ps.stem(word) for word in text.split()])

        # Step 6: Lemmatize each word of the text
        text = ' '.join([lmtzr.lemmatize(word, 'v') for word in text.split()])

        # Step 7: Remove extra spaces
        text = ' '.join(text.split())

    # return the cleaned text
    return text


def fetch_sentiment(text):
    """
    Fetch the sentiment of the text
    :param text: text to fetch the sentiment for
    :return: probability of the negative sentiment
    """

    # clean the text
    text = clean_text(text, deep=False)

    # encode the text
    encoded_input = tokenizer(text, return_tensors='pt')

    # fetch the sentiment
    output = model(**encoded_input)

    # get probability of each sentiment of the negative
    prob = softmax(output[0].detach().numpy(), axis=1)[0, 0]

    # return the probability of the negative sentiment
    return prob
