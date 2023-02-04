from newsapi import NewsApiClient
import tweepy
from geopy.geocoders import GoogleV3

import os
from tqdm import tqdm

from prophet.serialize import model_from_json
import numpy as np
from pickle import load
import joblib
# from keras.models import load_model
import requests
from datetime import datetime


def fetch_response(url):
    """
    Fetch the response from the given url
    :param url: url to fetch the response from
    :return: response
    """
    response = requests.get(url)
    response = response.json()
    return response


def init(bearer_token, news_api, api_key):
    """
    Initialize the API objects
    :param bearer_token: Twitter Bearer Token
    :param news_api: News API key
    :param api_key: Google API key
    :return: api, newsapi, geolocator

    api: tweepy.API object
    newsapi: NewsApiClient object
    geolocator: GoogleV3 object
    """

    # create an OAuthHandler object and set the access token and access token secret
    auth = tweepy.OAuth2BearerHandler(bearer_token=bearer_token)

    # create an API object using the auth object
    twitter_api = tweepy.API(auth)

    # create a newsapi object using the api key
    newsapi = NewsApiClient(api_key=news_api)

    # create a geolocator object using the api key
    geolocator = GoogleV3(api_key=api_key)

    # return the objects to be used in the main function
    return twitter_api, newsapi, geolocator


def fetch_locale(geocoder, lat, lng):
    """
    Fetch the locale of the given coordinates
    :param geocoder: GoogleV3 object
    :param lat: latitude
    :param lng: longitude
    :return: locale
    """

    # reverse geocode the coordinates to get the locale
    res = geocoder.reverse(f"{lat},{lng}")

    # get the sublocality name (town) from the response object
    sub_locality = [r['long_name'] for r in res.raw['address_components']
                    if 'sublocality_level_1' or 'administrative_area_level_1' in r['types']][0].split()[0]

    # get the locality name (city) from the response object
    locality = [r['long_name'] for r in res.raw['address_components']
                if 'locality' in r['types']][0].split()[0]

    return sub_locality, locality


def fetch_tweets(api, geocode, sub_locality, locality, threats, since, until):
    """
    Fetch the tweets from the given locale
    :param api: tweepy.API object
    :param sub_locality: sublocality name
    :param locality: locality name
    :param threats: list of threats to search for in the tweets (keywords)
    :param since: start date
    :param until: end date
    :return: tweets
    """

    # create a list to store the tweets
    texts = []
    steps = 15

    # fetch the tweets from the given locale
    for loc in tqdm([sub_locality, locality, ""], desc="Fetching tweets"):
        for i in range(0, len(threats), steps):
            # OR operator to search for multiple keywords
            keywords = " OR ".join(threats[i:i + steps])

            # fetch 5 tweets at a time to avoid rate limit  error
            # (15 requests per 15 minutes) and to avoid duplicate
            # tweets (max 100 tweets per request)
            tweets = api.search_tweets(
                q=f"{loc} {keywords} -filter:retweets",
                geocode=geocode if loc == "" else None,
                since_id=since,
                until=until,
                lang='en',
                tweet_mode='extended',
                count=5)

            # append the tweets to the list
            for tweet in tweets:
                texts.append(tweet if type(tweet) == str else tweet.full_text)

            break

    # return the tweets
    return texts


def fetch_news(newsapi, locality, threats, since, until):
    """
    Fetch the news articles from the given locale
    :param newsapi: NewsApiClient object
    :param locality: locality name
    :param threats: list of threats to search for in the news articles (keywords)
    :param since: start date
    :param until: end date
    :return: news articles
    """

    # create a list to store the news articles
    texts = []

    # fetch the news articles from the given locale
    for loc in tqdm([locality], desc="Fetching news"):
        for i in range(0, len(threats), 5):
            # OR operator to search for multiple keywords
            keywords = " OR ".join(threats[i:i + 5])

            # fetch the news articles from the given locale
            all_articles = newsapi.get_everything(q=f'{loc} AND ({keywords})',
                                                  from_param=since,
                                                  to=until,
                                                  language='en',
                                                  sort_by='relevancy',
                                                  page=1)

            # append the news articles to the list
            for article in all_articles['articles']:
                texts.append(article['description'])

            break

    # return the news articles
    return texts


def model_threat(lat, lng, TOMTOM_API, WEATHER_API):
    """
    Model the threat level for the given coordinates
    :param lat: latitude
    :param lng: longitude
    :return: threat level
    """

    TOMTOM = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"  # TomTom API
    WEATHER = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"  # weather API
    LOCATION = f"{lat},{lng}"  # coordinates of the location

    now = datetime.now()  # current date and time
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")  # 2020-12-01 12:00:00
    # 2020-12-01T12:00:00
    k = current_time.split(' ')[0]+'T'+current_time.split(' ')[1]

    # URL for TomTom API
    tomtom_url = f"{TOMTOM}?key={TOMTOM_API}&point={LOCATION}"
    # URL for Weather API
    weather_url = f"{WEATHER}/{LOCATION}/{k}?key={WEATHER_API}&include=current"
    # fetch the response from TomTom API
    traffic_response = fetch_response(tomtom_url)
    # fetch the response from Weather API
    weather_response = fetch_response(weather_url)

    BASE = "./models"  # base path for the models
    # load the traffic model from the json file using keras library (model_from_json)
    traffic_model = model_from_json(
        open(f'{BASE}/traffic_prophet_model.json', 'r').read())
    # load the weather model from the joblib file using joblib library
    weather_model = joblib.load(f"{BASE}/weather_model.joblib")
    # load the weather scaler from the pickle file using pickle library (load)
    scaler_weather = load(open(f'{BASE}/scaler_weather_model.pkl', 'rb'))
    # load the threat model from the h5 file using keras library (load_model)
    # Threat_model = load_model(f"{BASE}/score_pickle_model.h5")

    # create a dataframe for the future predictions of traffic model and weather model
    future = traffic_model.make_future_dataframe(periods=1)
    # take the last row of the dataframe as the future prediction is only for the next hour
    future = future.tail(1)
    future['Avgspeed'] = traffic_response['flowSegmentData']['currentSpeed'] / \
        traffic_response['flowSegmentData']['freeFlowSpeed']  # add the current speed of the road to the dataframe as a feature for the traffic model
    # predict the traffic level for the next hour using the traffic model
    forecast = traffic_model.predict(future)
    # store the predicted traffic level in preds_1 variable
    preds_1 = forecast['yhat']

    # create an array of the weather features for the weather model prediction (humidity, precipitation, windspeed)
    a = np.array([weather_response['days'][0]['humidity'], weather_response['days']
                 [0]['precip'], weather_response['days'][0]['windspeed']])
    # predict the weather level for the next hour using the weather model and store it in preds_2 variable (0: sunny, 1: cloudy, 2: rainy)
    preds_2 = weather_model.predict([a])
    # scale the weather level using the weather scaler and store it in preds_2 variable (0: sunny, 1: cloudy, 2: rainy)
    preds_2 = scaler_weather.transform(preds_2.reshape(-1, 1))
    # predict the threat level using the threat model and store it in k variable (0: low, 1: medium, 2: high)
    # k = Threat_model.predict([preds_1, preds_2], verbose=0)

    # return k[0][0]
    # return the mean of the traffic level and weather level
    return np.mean([np.mean(preds_1), np.mean(preds_2)]) / 100
