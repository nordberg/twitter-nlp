# -*- coding: utf-8 -*-
from twython import Twython, TwythonRateLimitError
from collections import Counter
import sys
import re


# Collects tweets for a specific hashtag from Twitter and parses them to 
# remove some special characters
# This method is used by toFile.py


client_args = {
	"headers": {
	"accept-charset": "utf-8"
	}
}

APP_KEY = 'BDFjwtDbPqCT07N6k4h6yaK9D'  # Customer Key here
APP_SECRET = 'DaNCLGNlw1sOuZrlBUTGoRPW99pH3vlkhQuxOTJXUherwPwtZY'
ACCESS_TOKEN = '335495642-WkhVdvjhipAWAbbqHrK0aWcOY7fIUC1ARynhEbit'
ACCESS_SECRET = 'dzo6CLq2JY6WNSooINBEl0yH5AYpdHcYq12Y2CXKALN7I'

def get_tweets(hashtag, tweetCount):
	twitter = Twython(APP_KEY, APP_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
	tweets = []
	corpora = ''
	wordCnt = Counter()
	# Max amount of queries is 15
	MAX_ATTEMPTS = 15
	counter =0
	for i in range(0, MAX_ATTEMPTS):
		if tweetCount <= len(tweets):
			break # found all tweets

		
		if (i == 0):
			results = twitter.search(q=hashtag, count=tweetCount - len(tweets), lang='en')
		else:
			results = twitter.search(q=hashtag, count=tweetCount - len(tweets), lang='en', include_entities='true', max_id=next_max_id)
		
		for result in results['statuses']:
			
			tweet = str(result['text'].encode(sys.stdout.encoding, errors='ignore'))
			#Remove poster's address
			tweet = re.sub('@[A-Za-z_0-9:]+ ', ' ', str(result['text'].encode(sys.stdout.encoding, errors='ignore')))
	
			#Removal of special Twitter symbols
			tweet = re.sub('(RT|RT |RT:|RT :|RT  :)', '', tweet)
			tweet = re.sub('b\'', '', tweet)
			tweet = re.sub('b"', '', tweet)

			tweet = re.sub('\w\\?\\[A-Za-z0-9]* ', ' ', tweet)
			tweet = re.sub('&amp;', ' ', tweet)
			tweet = re.sub('&gt', '>', tweet)
			tweet = re.sub('\\n', ' ', tweet)
			tweet = re.sub('\n', ' ', tweet)
			tweet = tweet.replace("\n", ' ') #Does the work for some reason
			tweet = tweet.replace("\\n", ' ') #Does the work for some reason
			tweet = re.sub('\\*\\n/g', ' ', tweet)
			tweet = re.sub('http[^\s]*', '', tweet) #matches all words that starts with http
			tweet = re.sub('\s\s+', ' ', tweet)
			tweet = tweet.strip() #Removes all leading and ending spaces
			
			#Remove ' and " at the end of a tweet
			if(tweet[-1]=='\'' or tweet[-1]=='"'):
				tweet = tweet[:len(tweet)-1]
			
			tweets.append(tweet.strip())
			corpora += tweet


		try:
			next_results_url_params = results['search_metadata']['next_results']
			next_max_id = next_results_url_params.split('max_id=')[1].split('&')[0]
		except:
			break

	return tweets, wordCnt, corpora
	
