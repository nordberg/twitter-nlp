# -*- coding: utf-8 -*-
from twython import Twython
import sys
import re

client_args = {
  "headers": {
    "accept-charset": "utf-8"
  }
}

APP_KEY = 'BDFjwtDbPqCT07N6k4h6yaK9D'  # Customer Key here
APP_SECRET = 'DaNCLGNlw1sOuZrlBUTGoRPW99pH3vlkhQuxOTJXUherwPwtZY'
ACCESS_TOKEN = '335495642-WkhVdvjhipAWAbbqHrK0aWcOY7fIUC1ARynhEbit'
ACCESS_SECRET = 'dzo6CLq2JY6WNSooINBEl0yH5AYpdHcYq12Y2CXKALN7I'

def main():
	for tweet in get_tweets('london', 200):
		print(tweet)

def get_tweets(hashtag, tweetCount):
	twitter = Twython(APP_KEY, APP_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
	results = twitter.search(q=hashtag, count=tweetCount)
	tweets = []
	for tweet in results['statuses']:
	        text = re.sub('@[A-Za-z]+', '', str(tweet['text'].encode(sys.stdout.encoding, errors='replace')))
	        text = re.sub('(RT|RT:|RT :|RT  :)', '', text)
	        text = re.sub('b\'', '', text)
	        text = re.sub(':|\\n', '', text)
	        text = re.sub('\\[A-Za-z0-9]* ', '', text)
	        text = re.sub('&amp;', '', text)
	        text = re.sub('\\n', '', text)
	        text = re.sub('\s\s+/g', ' ', text)
	        tweets.append(text)
	return tweets

main()