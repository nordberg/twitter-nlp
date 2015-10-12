import tweeter
import os.path

if __name__ == '__main__':
	hashtag = "test"
	numberOfTweets = 2000
	
	
	
	if os.path.isfile('tweet_' + hashtag):
		f = open('tweet_' + hashtag,'a') #append to file
	else :
		f = open('tweet_' + hashtag,'w') #create new file and write to
	

	for tweet in tweeter.get_tweets(hashtag, numberOfTweets)[0]:
		f.write(tweet + '\n')
	f.close()