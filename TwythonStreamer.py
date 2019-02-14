# Import the Twython class
from twython import Twython 
from twython import TwythonStreamer
import csv 
import json
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from textblob import TextBlob

from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, SentimentOptions ,EmotionOptions
import sys

# Load credentials from json file
with open("twitter_credentials.json", "r") as file:  
    creds = json.load(file)

natural_language_understanding = NaturalLanguageUnderstandingV1(
    version='2018-12-11',
    iam_apikey='2wmf5sIFDCin1NV5OZexjXtdr7BR2b_OVHA7oAn2Nfaa',
    url='https://gateway-fra.watsonplatform.net/natural-language-understanding/api'
    )

# Filter out unwanted data
def process_tweet(tweet):  
    d = {}
    #d['hashtags'] = [hashtag['text'] for hashtag in tweet['entities']['hashtags']]
    d['date']= tweet['created_at']
    d['user'] = tweet['user']['screen_name']
    d['user_loc'] = tweet['user']['location']
    d['text'] = tweet['text']
    d['lang']= tweet['lang']
    return d

# Create a class that inherits TwythonStreamer
class MyStreamer(TwythonStreamer):     

        # Received data
    def on_success(self, data):
        # Only collect tweets in English and non retweets
        #Twitter returns data in JSON format 
        tweet_data = process_tweet(data)
        cleaned_tweet_data = self.clean_tweet(tweet_data)
        if (not cleaned_tweet_data['text'].startswith('RT') and cleaned_tweet_data['lang'] == 'en' and 'Samsung' in cleaned_tweet_data['text']) :
            cleaned_tweet_data['sentiment'] = self.analyze_sentiment(cleaned_tweet_data)
            cleaned_tweet_data['emotion'] = self.analyze_emotion(cleaned_tweet_data)
            self.save_to_csv(cleaned_tweet_data)
            print(cleaned_tweet_data)

    # Error ocurring at the API
    def on_error(self, status_code, data):
        print(status_code, data)
        self.disconnect()

    #Removing hyperlinks in the text attribute
    def clean_tweet(self, tweet):
        cleaned_text = re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet['text'])
        tweet['text'] = cleaned_text
        return tweet

    # Save each tweet to csv file
    def save_to_csv(self, tweet):
        with open('analyzed_samsung_tweets.csv', 'a') as file:
            writer = csv.writer(file)
            writer.writerow(list(tweet.values()))

    #Analyze sentiment 
    def analyze_sentiment(self, tweet):
        if 'Samsung' in tweet['text'] :
            analysis = natural_language_understanding.analyze(
                text = tweet['text'],
                features= Features(sentiment= SentimentOptions(targets=['Samsung']))).get_result()

            analyzed = json.dumps(analysis['sentiment']['targets'][0]['score'])
          
            return analyzed
        else:
            return ' '
    
    #Analyze emotion
    def analyze_emotion(self, tweet):
        if 'Samsung' in tweet['text'] :

            analysis = natural_language_understanding.analyze(
               text= tweet['text'],
               features=Features(emotion=EmotionOptions(targets=['Samsung']))).get_result()
            heighest_score = max(analysis['emotion']['targets'][0]['emotion'], key= analysis['emotion']['targets'][0]['emotion'].get)
            return json.dumps(heighest_score)

        else:
            return ' '
# Instantiate from our streaming class
stream = MyStreamer(creds['CONSUMER_KEY'], creds['CONSUMER_SECRET'],  
    creds['ACCESS_TOKEN'], creds['ACCESS_SECRET'])

# Start the stream
stream.statuses.filter(track='Samsung', language='en')
