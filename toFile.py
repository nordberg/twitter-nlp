import tweeter
import os.path
import sys



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
	

	for tweet in tweeter.get_tweets(hashtag, numberOfTweets)[0]:
		if tweet + '\n' not in open(filename).read() :
			f.write(tweet + '\n')
	f.close()