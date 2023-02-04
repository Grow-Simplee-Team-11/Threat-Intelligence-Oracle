from concurrent import futures
import logging
from threat.utils import *
from threat.nlp import *

from datetime import datetime, timedelta
from dotenv import dotenv_values

import threat_pb2
import threat_pb2_grpc

import grpc
from grpc import StatusCode, RpcError  # for error handling


# list of threats to be searched for in the tweets and news articles (can be extended)
THREATS = [
    'traffic', 'heavy traffic',  'accident',  'snow',  'curfew', 'pandemic',  'covid', 'flood',
    'hurricane', 'fire', 'earthquake',  'tornado',  'volcano',  'tsunami',  'drought',  'hail',
    'fog', 'heat wave',  'avalanche',  'landslide',  'cyclone',  'tropical storm',  'blizzard',
    'thunderstorm',   'wildfire',  'rain',  'storm',  'heavy rain',  'lockdown',  'quarantine',
    'corona', 'road accident', 'road block', 'road jam', 'road closure', 'traffic jam', 'rush',
    'congestion', 'rush', 'construction', 'overcrowding', 'festivals', 'celebration',  'rally', 'riot', 'strike']

SHIFT = 10**6  # used to convert the coordinates to float


def scorer(lat, lng):
    today = datetime.now()  # get the current date
    # fetch tweets from the last 3 days
    yesterday = today - timedelta(days=3)

    # format the date to be used in the search query
    since_id = yesterday.strftime("%Y-%m-%d")  # since_id = "2020-12-01"
    until_id = today.strftime("%Y-%m-%d")  # until_id = "2020-12-04"

    config = dotenv_values('.env')  # load the environment variables
    twitter_api, newsapi, geolocator = init(
        config['BEARER_TOKEN'], config['NEWS_API'], config['API_KEY'])  # initialize the API objects

    # fetch the locale of the given coordinates
    sub_locality, locality = fetch_locale(geolocator, lat, lng)

    # fetch the tweets from the given locale
    try:
        tweets = fetch_tweets(
            twitter_api,
            f"{lat},{lng},20km",
            sub_locality,
            locality,
            THREATS,
            since_id,
            until_id)
    except Exception as e:
        raise RpcError(StatusCode.INTERNAL, "Internal Error")

    # fetch the news articles from the given locale
    try:
        news = fetch_news(
            newsapi,
            locality,
            THREATS,
            since_id,
            until_id)
    except Exception as e:
        raise RpcError(StatusCode.INTERNAL, "Internal Error")

    # get the average sentiment score
    score = 0
    for text in tweets + news:
        score = max(score, fetch_sentiment(text))

    return score + model_threat(lat, lng, config['TOMTOM_API'], config['WEATHER_API']) // 100 # add the threat score


class Threat(threat_pb2_grpc.ThreatServicer):
    def __init__(self, *args, **kwargs):
        pass

    def getThreatScore(self, request, context):
        lat = request.latitude  # "19.0765821802915"
        lng = request.longitude  # "72.8724884302915"

        if not isinstance(lat, int) or not isinstance(lng, int):
            context.set_code(StatusCode.INVALID_ARGUMENT)
            context.set_details("Invalid Argument")
            return threat_pb2.threatResponse()

        lat /= SHIFT
        lng /= SHIFT

        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            context.set_details("Invalid Argument")
            return threat_pb2.threatResponse()

        score = scorer(lat, lng)
        return threat_pb2.threatResponse(threat=score)


def serve():
    # set the port number
    port = '8080'

    # create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # add the defined class to the server
    threat_pb2_grpc.add_ThreatServicer_to_server(Threat(), server)

    # listen on port 8080
    server.add_insecure_port('[::]:' + port)

    # start the server
    server.start()
    print("Server started, listening on " + port)

    # keep the server running
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    serve()
