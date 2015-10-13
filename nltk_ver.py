import nltk
import os
import random
import sys
import re
from nltk.tag import StanfordPOSTagger

LOWER_CASE = True

#STANFORD AND JAVA SETUP
nltk.internals.config_java("C:\\Program Files (x86)\\Java\\jre1.8.0_60\\bin")
os.environ['JAVAHOME'] = "C:\\Program Files (x86)\\Java\\jre1.8.0_60\\bin"
path_to_model = os.getcwd()+'\\stanford-postagger-2015-04-20\\models\\english-left3words-distsim.tagger'
path_to_jar = os.getcwd()+'\\stanford-postagger-2015-04-20\\stanford-postagger.jar'
stanford = StanfordPOSTagger(path_to_model,path_to_jar)

grammar_cache = {}
single_grammar_cache = {}

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
              ngram_list.append((tuple([""]*(n-i) + input_list[0:max(0,i)]),input_list[i]))
      for i in range(n,len(input_list)):
          #Regular n-grams
          ngram_list.append((tuple(input_list[i-n:i]),input_list[i]))
      if none_fill:
          #None-fill at end
          for i in range(n):
              ngram_list.append((tuple(input_list[len(input_list)-n:len(input_list)-i]+[""]*i),""))
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

def get_grammar_ngrams(tweets,n):
    ''' converts the n-gram model into a grammar type model'''
    grammar = []
    tweets  = [t.split() for t in tweets]
    merged = []
    for t in tweets:
        merged += t + [""]*n
    g_grams = stanford.tag(merged)
    g_grams = [g[1] for g in g_grams]
    for w,g in zip(merged,g_grams):
        single_grammar_cache[w] = g
    grammar = find_ngrams(g_grams,n)
    for g in grammar[::-1]:
        if g[1] in [",",".","!","?"]:
            grammar.append(g)
    return grammar



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

def to_grammar(word):
    if word == "":
        return ""
    if single_grammar_cache.get(word):
        word_g = single_grammar_cache[word]
    else:
        try:
            word_g = stanford.tag(word)[1]
        except IndexError as e:
            print(e)
            return ""
        single_grammar_cache[word] = word_g
    return word_g

def white_space_puncation(tweet):
    tweet = re.sub(r"([\\,\\.\\?\\!])(\S)",r'\1 \2',tweet)
    tweet = re.sub(r"(\S)([\\,\\.\\?\\!])",r'\1 \2',tweet)
    return tweet

def fix_punctation(tweet):
    t1 = tweet
    for i in range(50):
        tweet = re.sub(r"([\S].)\s+([\\,\\.\\?\\!])",r'\1\2',tweet)
        if tweet == t1:
            break
    
    def uppercase(matchobj):
        return matchobj.group(0).upper()

    tweet = re.sub('^([a-z])|[\.|\?|\!]\s*([a-z])|\s+([a-z])(?=\.)', uppercase, tweet)
    return tweet

def generate_tweet(hashtag):

    # Settings
    avoid_copy = True
    check_length = 4
    n = 2
    g_n = 2

    # Gather the tweets
    tweets = [extra_trim(white_space_puncation(t)) for t in read_file(hashtag)]
    if LOWER_CASE: tweets = [t.lower() for t in tweets]

    if grammar_cache.get(hashtag):
        g_grams = grammar_cache[hashtag]
    else:
        print("Creating grammar")
        g_grams = get_grammar_ngrams(tweets,g_n)
        grammar_cache[hashtag] = g_grams
        print("Grammar done")

    
    # Create probability model
    grams = create_model(tweets,n)
    cfd = nltk.ConditionalFreqDist(grams)
    grammar = nltk.ConditionalFreqDist(g_grams)

    # Init loop values
    last = [""]*n
    new_word = ""
    sentence = []

    #Each iteration produces 1 word
    for i in range(50):
        as_tuple = tuple(last)
        as_grammar = [""]*max(0,len(sentence)-g_n) + sentence[-g_n:]
        as_grammar = tuple(as_grammar)

        # Get the 10 most common successors for the current n last words
        choices = cfd[as_tuple].most_common(15)
        best_grammar = grammar[as_grammar].most_common(3)
       # print("best",best_grammar)
        if len(choices) == 0:
            # Stop if no choices are available
            # We want smoothing here!
            break

        # Tries to find a plagiary substring choice 20 times 
        for j in range(20):
            new_word = random.choice(choices)[0] #Get a random successor

            if len(sentence) > 0:
                new_word_g = to_grammar(new_word)
                if len(best_grammar) > 0:
                    if all(new_word_g != best_g[0] for best_g in best_grammar):
                        continue
            # Special case - only allow sentences to beging with
            # alphabetical characters or hashtags
            if len(sentence) == 0 and re.sub("#","",new_word).isalpha():
                break

            # When the substring length for plagiary check is reached
            # start check the sentence.
            if len(sentence) >= check_length:
                if new_word == "":
                    if choices[0][0] == "":
                        # Only end tweet if it is the most popular alternative
                        continue
                    if not is_copy(" ".join(sentence),tweets):
                        # If the entire sentence is unique, allow it.
                        break
                elif not is_copy(" ".join((sentence+[new_word])[-check_length:]),tweets):
                    # If the number of words given by check_length is not a substring of
                    # any tweet, allow the choice.
                    break

        if new_word == "":
            #End of tweet was selected, abort appending
            break

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
        pass#tweet += "."
    if tweet[0].isalpha() and tweet[0].lower() == tweet[0]:
        tweet = tweet[0].upper()+tweet[1:]
    tweet = re.sub(r" i "," I ",tweet)
    tweet = fix_punctation(tweet)
    return tweet

def read_file(hashtag):
    '''Reads all tweets from a file given the naming convention'''
    with open(os.getcwd()+'\\tweet_'+hashtag) as f:
        lines = f.read().splitlines()
    return lines

tweets = []
while len(tweets) < 10:
    cpy,chars,tweet = generate_tweet("weird")
    if not cpy and chars < 141:
        tweets.append(tweet)
        print(tweet)