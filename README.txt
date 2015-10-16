# README
tweet_generator.py is the main program and the "brain" behind our implementation. As it is python but uses java, it is 
necessary that the java path is set up correctly.

On line 15-17 of tweet_generator.py, the java path is configured. It is important that the java_path variable is set to the 
bin folder path of the JRE.

FOR LINUX:
	It is enough to call the function nltk.internals.config_java(), it will find the java path (/usr/bin/java) automatically

FOR WINDOWS
	The path to java has to be provided in the nltk.internals.config_java() function call.

DEPENDENCIES:
	Python 3.X
	to run tweeter.py you need to install
		twython
	to run tweet_generator you need to install
		nltk
	to run results_analysis you need to install
		numpy
		scipy
		pandas
		matplotlib
	to install:
		pip install <package>
	note that pip will install all additional dependencies for the packages.


After this, the program can be run with Python 3.X. It does not work with Python 2.X. Note that the databases are provided 
in the format "tweet_<hashtag>" where hashtag can be one of the following: Apple, obama, coding, halloween, dude, hockey, news, random, or weird.

To change the hashtag used for generating the tweets, change the "hashtag" variable in the main function at the end of tweet_generator.py or send the hastag as an argument.

The secondary program is the 'turing.py' file which contains the test environment. Simply run it as python program. 
It takes one (optional) parameter: how many tweets to be tested. If no parameter is provided, it will display 30 tweets 
and let the user type c for computer and h for human. All answers are gathered in a file (named results.py) in a format
which allows us to perform some data analysis.
 
Other files are:
tweeter.py				collects tweets from Twitter, using twython
toFile.py				puts the collected tweets in a file named tweet_[hashtag]
test_10x10_1.py			contains the 200-tweet database used in the Turing tests
results_analysis.py		creates a summary of the result data from the test

results.py 				Data file. Contains the raw result data from the Turing test
tweet_[hashtag]			Data files. Contains the hashtags collected from Twitter

Map:
stanford-postagger-2015-04-20	Used for grammar tagging

				
 

