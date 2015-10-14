import os
import sys
import random
import nltk_ver

nr_of_tweets = 3

def main():
	print('Hello and welcome to this test! You will be presented ' + str(nr_of_tweets) + ' tweets. ' + \
		'Please type \'C\' or \'c\' if you think it is a computer generated tweet and \'H\' or \'h\' ' + \
		'if you think it is a tweet written by a human. Please note that it is not guaranteed that it' + \
		' is an even distribution of the two.')
	print('-----------------------------------')

	import test_10x10_1
	tweets = test_10x10_1.all_tweets
	h_tweets = [t for t in tweets if t[0]]
	c_tweets = [t for t in tweets if not t[0]]

	c_number = random.randint(0,nr_of_tweets)
	human_tweets = random.sample(h_tweets,nr_of_tweets-c_number)
	computer_tweets = random.sample(c_tweets,c_number)
	test_sample = human_tweets+computer_tweets
	random.shuffle(test_sample)
	was_right = []

	result_file = "results.py"
	with open(result_file, "a") as f:
		for i,tweet in enumerate(test_sample):
			print('Tweet Nr. ' + str(i + 1) + " #"+tweet[1])
			print(tweet[2])
			print('C/c (Computer) or H/h (Human)?')

			choice = None
			while choice not in ['c','C','h','H']:
				choice = input('Guess: ')
			human_guess = choice.lower() == 'h'
			if human_guess:
				was_right.append(tweet[0])
			else:
				was_right.append(not tweet[0])
			print("answers.append("+str((human_guess,tweet))+")",file=f)

	print("-------------------------------------------------------------")
	print("-------------------------------------------------------------")
	print("-------------------------------------------------------------")
	print()
	print("You scored " + str(was_right.count(True)) + "/"+str(nr_of_tweets))
	for score,tweet in zip(was_right,test_sample):
		print("Origin: " + ("H" if tweet[0] else "C") + ". Score: " + ("CORRECT" if score else "WRONG"))
		print("#"+ tweet[1] + " " + tweet[2])

	print("THANK YOU FOR PARTICIPATING")
	input()



if __name__ == '__main__':
	main()