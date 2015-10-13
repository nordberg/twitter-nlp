import tweeter
import os.path
import sys
from twython import TwythonRateLimitError

# This is the main method for extracting tweets from twitter 
# and putting them in a file with name: tweet_[hashtag]
#
# You can specify hashtag using the method argument, if no hashtag is specified the 
# default hashtag will be chosen
# If tweets for the specified hashtag already exists this method will append new tweets
# to the same file
# This method will never add two exactly identical tweets
# The maximum number of tweets you can collect from Twython at the same time is 1500

if __name__ == '__main__':
	if len(sys.argv)>1 :
		hashtag = sys.argv[1]
	else :
		hashtag = "obama"
	numberOfTweets = 1500
	
	
	filename = 'tweet_' + hashtag
	
	
	if os.path.isfile(filename):
		f = open(filename,'a') #append to file
	else :
		f = open(filename,'w') #create new file and write to
	

	#while True: Twython only gets the lastest tweets, so calling the function 
	#multiple times does nothing. You have to wait
	try :
		for tweet in tweeter.get_tweets(hashtag, numberOfTweets)[0]:
			if tweet + '\n' not in open(filename).read() :
				f.write(tweet + '\n')
			f = open(filename,'a')
	except TwythonRateLimitError:
		print ("Rate limit error")
		print( twitter.get_lastfunction_header('x-rate-limit-limit'))
		print( twitter.get_lastfunction_header('x-rate-limit-remaining'))
		print( twitter.get_lastfunction_header('x-rate-limit-class'))
		print( twitter.get_lastfunction_header('x-rate-limit-reset'))
		sys.exit()
	#f.close()