import os
import sys
import random
import nltk_ver

nr_of_tweets = 20

def main():
	print('Hello and welcome to this test! You will be presented ' + str(nr_of_tweets) + ' tweets. ' + \
		'Please type \'C\' or \'c\' if you think it is a computer generated tweet and \'H\' or \'h\' ' + \
		'if you think it is a tweet written by a human. Please note that it is not guaranteed that it' + \
		' is an even distribution of the two.')
	print('-----------------------------------')

	hashtag = 'obama'
	human_tweets = fill_human_tweets(hashtag)
	computer_tweets = fill_computer_tweets(hashtag)

	right = 0

	for i in range(nr_of_tweets):
		print('Tweet Nr. ' + str(i + 1))
		r = random.randint(0, 1)
		if r == 0:
			print(human_tweets[i])
		else:
			print(computer_tweets[i])
		print('C/c (Computer) or H/h (Human)?')

		choice = raw_input('Answer: ')
		if r == 0:
			if choice.lower() == 'h':
				right += 1
			else:
				print('Wrong!')
		if r == 1:
			if choice.lower() == 'c':
				right += 1
			else:
				print('Wrong!')

	print('You got ' + str(right) + ' out of ' + str(nr_of_tweets) + ' correct!')

def fill_human_tweets(hashtag):
	with open(os.getcwd()+os.path.sep+'tweet_'+hashtag) as f:
		lines = f.read().splitlines()

	tweets = []

	for i in range(nr_of_tweets):
		tweets.append(lines[random.randint(0, len(lines))])

	return tweets

def fill_computer_tweets(hashtag):
	tweets = []

	for i in range(nr_of_tweets):
		tweets.append(nltk_ver.get_tweet(hashtag))

	return tweets

main()