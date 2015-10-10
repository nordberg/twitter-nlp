# -*- coding: utf-8 -*-
from twython import Twython
from collections import Counter
import sys
import re
import markovify

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
	a, b, c = get_tweets('android', 100)
	print('received tweets')
	#text_model = markovify.Text(c)
	print('generated text model')
	#print(text_model.make_short_sentence(140))

def get_tweets(hashtag, tweetCount):
	twitter = Twython(APP_KEY, APP_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
	results = twitter.search(q=hashtag, count=tweetCount)
	wordCnt = Counter()
	corpora = ''
	tweets = []
	p = re.compile('[A-Za-z0-9]')
	for tweet in results['statuses']:
			'''text = re.sub('@[A-Za-z]+', '', str(tweet['text'].encode(sys.stdout.encoding, errors='ignore')))
			text = re.sub('(RT|RT:|RT :|RT  :)', '', text)
			text = re.sub('b\'', '', text)
			text = re.sub('\\n', '', text)
			text = re.sub('\w\\?\\[A-Za-z0-9]* ', '', text)
			text = re.sub('&amp;', '', text)
			text = re.sub('\\*\\n/g', '', text)
			text = re.sub('\s\s+/g', ' ', text)
			text = re.sub('https?://\w*\.co/\w*', '', text)'''
			text = str(tweet['text'].encode(sys.stdout.encoding, errors='ignore'))
			print(p.group(p.match(text)))
			tweets.append(text)
			corpora += ' '
			corpora += text
			for word in text.split():
				wordCnt[word] += 1
	return tweets, wordCnt, corpora

main()