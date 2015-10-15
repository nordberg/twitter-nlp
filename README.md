# README
nltk_ver.py is the main program and the "brain" behind our implementation. As it is python but uses java, it is necessary that the java path is set up correctly.

On line 15-17 of nltk_ver.py, the java path is configured. It is important that the java_path variable is set to the bin folder path of the JRE.

FOR LINUX:
	It is enough to call the function nltk.internals.config_java(), it will find the java path (/usr/bin/java) automatically

FOR WINDOWS
	The path to java has to be provided in the nltk.internals.config_java() function call.

After this, the program can be run with Python 3.X. It does not work with Python 2.X. Note that the databases are provided in the format "tweet_hashtag" where hashtag can be one of the following: Apple, obama, coding, halloween, dude, hockey, news, random, or weird.

To change the hashtag used for generating the tweets, change the "hashtag" variable in the main function at the end of nltk_ver.py.

The secondary program is the 'turing.py' file which contains the test environment. Simply run it as python program. It takes one (optional) parameter: how many tweets to be tested. If no parameter is provided, it will display 30 tweets and let the user type c for computer and h for human. All answers are gathered in a file (named results.py) in a format which allows us to perform some data analysis.