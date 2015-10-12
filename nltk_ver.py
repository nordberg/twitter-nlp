import nltk
import os
import random
import sys
import re

LOWER_CASE = True

def find_ngrams(input_list,n,none_fill = True):
    '''
    Returns a list of ((n-gram),next_gram) for the input string.
    Also adds ngrams containing None for start and end of sentences  
    '''
  ngram_list = []
  try:
      if none_fill:
          #None-fill at start
          for i in range(n):
              ngram_list.append((tuple([None]*(n-i) + input_list[0:max(0,i)]),input_list[i]))
      for i in range(n,len(input_list)):
          #Regular n-grams
          ngram_list.append((tuple(input_list[i-n:i]),input_list[i]))
      if none_fill:
          #None-fill at end
          for i in range(n):
              ngram_list.append((tuple(input_list[len(input_list)-n:len(input_list)-i]+[None]*i),None))
  except IndexError:
      return []
  return ngram_list

def create_model(tweets,n):
    ''' Merges all n-grams of all tweets'''
    split_t = [t.split() for t in tweets]
    model = []
    for tweet in split_t:
        grams = find_ngrams(tweet,n)
        model += grams
    return model

def is_copy(tweet, database):
    '''check if the tweet is a substring of any string in the database list'''
    if LOWER_CASE:
        return any(tweet in t.lower() for t in database)
    else:
        return any(tweet in t for t in database)


def extra_trim(tweet):
    '''Makes small hacks on the tweets'''
    if(tweet[-1] == "'"):
        tweet = tweet[:-1]
    tweet = re.sub("\n"," ",tweet)
    return tweet

def generate_tweet(hashtag):

    # Settings
    avoid_copy = True
    check_length = 6
    n = 2

    # Gather the tweets
    tweets = [extra_trim(t) for t in read_file(hashtag)]
    if LOWER_CASE: tweets = [t.lower() for t in tweets]
    
    # Create probability model
    grams = create_model(tweets,n)
    cfd = nltk.ConditionalFreqDist(grams)

    # Init loop values
    last = [None]*n
    new_word = None
    sentence = []

    #Each iteration produces 1 word
    for i in range(50):
        as_tuple = tuple(last)

        # Get the 10 most common successors for the current n last words
        choices = cfd[as_tuple].most_common(10) 
        if len(choices) == 0:
            # Stop if no choices are available
            # We want smoothing here!
            break

        # Tries to find a plagiary substring choice 20 times 
        for j in range(20):
            new_word = random.choice(choices)[0] #Get a random successor

            # Special case - only allow sentences to beging with
            # alphabetical characters or hashtags
            if len(sentence) == 0 and not re.sub("#","",new_word).isalpha():
                continue

            # When the substring length for plagiary check is reached
            # start check the sentence.
            if len(sentence) >= check_length:
                if new_word == None:
                    if choices[0][0] == None:
                        # Only end tweet if it is the most popular alternative
                        continue
                    if not is_copy(" ".join(sentence),tweets):
                        # If the entire sentence is unique, allow it.
                        break
                elif not is_copy(" ".join((sentence+[new_word])[-check_length:]),tweets):
                    # If the number of words given by check_length is not a substring of
                    # any tweet, allow the choice.
                    break

        if new_word == None:
            #End of tweet was selected, abort appending
            break

        #Append to sentence and update last n-gram
        sentence.append(new_word)
        last = last[1:]
        last.append(new_word)

    sent = " ".join(sentence)

    # Make some symbol correction
    corr_sent = sent
    double = corr_sent.count('"')
    lpar = corr_sent.count('(')
    rpar = corr_sent.count(')')
    #single = corr_sent.count("'")
    if double == 1: corr_sent = re.sub('"',"",corr_sent)
    if lpar == 1: corr_sent = re.sub(r'\(',"",corr_sent)
    if rpar == 1: corr_sent = re.sub(r'\)',"",corr_sent)
    #if single == 1: corr_sent = re.sub('"',"")
    if corr_sent[-1] not in [".",",","?","!"] :
        corr_sent += "."

    #print the result
    print(is_copy(sent,tweets),len(sent))
    print(sent)
    print(corr_sent)
 #   for word in cfd.conditions():
 #       print(word,cfd[word])
    #  print(generate_model(cfd, " ".split(random.choice(tweets))[0]))


def read_file(hashtag):
    '''Reads all tweets from a file given the naming convention'''
    with open(os.getcwd()+'\\tweet_'+hashtag) as f:
        lines = f.read().splitlines()
    return lines

for i in range(10):
    generate_tweet("happy")
    print()