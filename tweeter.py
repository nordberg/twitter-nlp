# -*- coding: utf-8 -*-
from twython import Twython
from collections import Counter
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

def get_tweets(hashtag, tweetCount):
	twitter = Twython(APP_KEY, APP_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
	tweets = []
	corpora = ''
	wordCnt = Counter()
	# Max amount of queries is 15
	MAX_ATTEMPTS = 15
	for i in range(0, MAX_ATTEMPTS):
		if tweetCount <= len(tweets):
			break # found all tweets

		if (i == 0):
			results = twitter.search(q=hashtag, count=tweetCount - len(tweets), lang='en')
		else:
			results = twitter.search(q=hashtag, count=tweetCount - len(tweets), lang='en', include_entities='true', max_id=next_max_id)

		for result in results['statuses']:
			tweet = result['text']
			tweet = re.sub('@[A-Za-z]+', ' ', str(result['text'].encode(sys.stdout.encoding, errors='ignore')))
			tweet = re.sub('(RT|RT:|RT :|RT  :)', ' ', tweet)
			tweet = re.sub('b\'', ' ', tweet)
			tweet = re.sub('\w\\?\\[A-Za-z0-9]* ', ' ', tweet)
			tweet = re.sub('&amp;', ' ', tweet)
			tweet = re.sub('\\n', ' ', tweet)
			tweet = re.sub(':', ' ', tweet)
			tweet = re.sub('\\*\\n/g', ' ', tweet)
			tweet = re.sub('https?://\w*\.co/\w*', '', tweet)
			tweet = re.sub('b"', ' ', tweet)
			tweet = re.sub('\s\s+', ' ', tweet)
			

			if(tweet[-1]=='\'' or tweet[-1]=='"'):
				tweet = tweet[:len(tweet)-1]
			tweets.append(tweet.strip())
			corpora += tweet
			for word in tweet.split():
				wordCnt[word] += 1

		try:
			next_results_url_params = results['search_metadata']['next_results']
			next_max_id = next_results_url_params.split('max_id=')[1].split('&')[0]
		except:
			break

	return tweets, wordCnt, corpora
	
