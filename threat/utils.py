from newsapi import NewsApiClient
import tweepy
from geopy.geocoders import GoogleV3

from tqdm import tqdm


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
    res = geocoder.reverse(lat + "," + lng)

    # get the sublocality name (town) from the response object
    sub_locality = [r['long_name'] for r in res.raw['address_components']
                    if 'sublocality_level_1' in r['types']][0].split()[0]

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
