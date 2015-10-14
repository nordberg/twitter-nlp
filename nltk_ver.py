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
    split_t = [t.split() for t in tweets if "\\" not in t and "http" not in t]

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
    tweet = re.sub("\\n"," ",tweet)
    return tweet

def generate_tweet(hashtag):

    # Settings
    avoid_copy = True
    n = 3
    check_length = 2;

    # Gather the tweets
    tweets = [extra_trim(t) for t in read_file(hashtag)]
    if LOWER_CASE: tweets = [t.lower() for t in tweets]

    cfds = [];
    cfds.append(None)

    # Train models for all n-grams that could be used
    for x in range(1, n+1):
        # Create probability model
        grams = create_model(tweets,x)
        cfd = nltk.ConditionalFreqDist(grams)
        cfds.append(cfd)

    # Init loop values
    last = [None]*n
    new_word = None
    sentence = []

    #Each iteration produces 1 word
    for i in range(50):
        as_tuple = tuple(last)

        found = False
        # Start with a n-gram and decrease to 2-gram if no word was found
        for k in range (n, 1, -1):
            if found:
                break;
            # Get the 10 most common successors for the current n last words
            choices = cfds[k][as_tuple].most_common(2000)
            #new_word = random.choice(choices)[0] #Get a random successor

            #print(len(choices))
            #if len(choices) < 2:
             #   continue
            #if all(occ[1] < 10 for occ in choices):
            #   continue
            if len(choices) > 0:
                # Stop if no choices are available
                # We want smoothing here!
                #break

                # Tries to find a plagiary substring choice 20 times 
                for j in range(20):
                    if found:
                        break
                    new_word = random.choice(choices)[0] #Get a random successor

                    # Special case - only allow sentences to beging with
                    # alphabetical characters or hashtags
                    if len(sentence) == 0 and re.sub("#","",new_word).isalpha():
                        found = True

                    # When the substring length for plagiary check is reached
                    # start check the sentence.
                    if len(sentence) >= check_length:
                        if new_word == None:
                            if choices[0][0] == None:
                                # Only end tweet if it is the most popular alternative
                                found = True
                            if not is_copy(" ".join(sentence),tweets):
                                # If the entire sentence is unique, allow it.
                                found = True
                        elif not is_copy(" ".join((sentence+[new_word])[-check_length:]),tweets):
                            # If the number of words given by check_length is not a substring of
                            # any tweet, allow the choice.
                            found = True

            print("N-gram used: ")
            print(k)

        if new_word == None:
            #End of tweet was selected, abort appending
            break

        print("N-gram used: ")
        print(k)
        print(i,k,j,new_word, len(sentence))
        #Append to sentence and update last n-gram
        sentence.append(new_word)
        last = last[1:]
        last.append(new_word)

    sent = " ".join(sentence)

    # Make some symbol correction
    corr_sent = fix_tweet(sent)

    #print the result
    return (is_copy(sent,tweets),len(sent),corr_sent)
 #   for word in cfd.conditions():
 #       print(word,cfd[word])
    #  print(generate_model(cfd, " ".split(random.choice(tweets))[0]))

def fix_tweet(tweet):
    double = tweet.count('"')
    lpar = tweet.count('(')
    rpar = tweet.count(')')
    if double == 1: tweet = re.sub('"',"",tweet)
    if lpar == 1: tweet = re.sub(r'\(',"",tweet)
    if rpar == 1: tweet = re.sub(r'\)',"",tweet)
    #if single == 1: corr_sent = re.sub('"',"")
    if tweet[-1] not in [".",",","?","!"] :
        tweet += "."
    if tweet[0].isalpha() and tweet[0].lower() == tweet[0]:
        tweet = tweet[0].upper()+tweet[1:] 
    return tweet

def read_file(hashtag):
    '''Reads all tweets from a file given the naming convention'''
    with open(os.getcwd()+os.path.sep+'tweet_'+hashtag) as f:
        lines = f.read().splitlines()
    return lines

def produce_word(last, cfds):
    return word;



tweets = []
while len(tweets) < 1:
    cpy,chars,tweet = generate_tweet("hockey")
    if not cpy and chars > 30 and chars < 141:
        tweets.append(tweet)
for t in tweets:
    print(t)
    
