import tweeter

if __name__ == '__main__':
	hashtag = "obama"
	numberOfTweets = 2000
	f = open('tweet_' + hashtag,'w')
	for tweet in tweeter.get_tweets(hashtag, numberOfTweets)[0]:
		f.write(tweet)
		f.write('\n')
	f.close()