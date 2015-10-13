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
model_cache = {}

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

    #Make all tweets into a single list, add n None between each tweet
    for t in tweets:
        merged += t + [""]*n

    # Run the Grammar tagging
    g_grams = stanford.tag(merged)
    g_grams = [g[1] for g in g_grams]

    # Create a map for word to grammar type (major speed increase)
    for w,g in zip(merged,g_grams):
        single_grammar_cache[w] = g

    # Create g-grams
    grammar = find_ngrams(g_grams,n)

    #Double chance for punctation
    #for g in grammar[::-1]:
    #    if g[1] in [",",".","!","?"]:
    #        grammar.append(g)
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

def is_probable_grammar(new_word, best_grammar):
    new_word_g = to_grammar(new_word)
    if len(best_grammar) == 0:
        return True
    if all(new_word_g != best_g[0] for best_g in best_grammar):
        return False
    return True

def generate_tweet(hashtag):

    # Settings
    n = 3
    g_n = 3

    # Gather the tweets
    tweets = [extra_trim(white_space_puncation(t)) for t in read_file(hashtag)]
    if LOWER_CASE: tweets = [t.lower() for t in tweets]

    # Create Grammar
    if grammar_cache.get(hashtag):
        g_grams = grammar_cache[hashtag]
    else:
        print("Creating grammar")
        g_grams = get_grammar_ngrams(tweets,g_n)
        grammar_cache[hashtag] = g_grams
        print("Grammar done")

    #Create n-gram model
    if model_cache.get(hashtag):
        grams = model_cache[hashtag]
    else:
        print("Creating model")
        grams = create_model(tweets,n)
        model_cache[hashtag] = grams
        print("model done")

    
    # Create probability model
    cfd = nltk.ConditionalFreqDist(grams)
    grammar = nltk.ConditionalFreqDist(g_grams)
    fqd = nltk.FreqDist()
    for g in grams:
        fqd[g[0]] += 1

    knd = nltk.probability.KneserNeyProbDist(fqd)

    # Init loop values
    last = [""]*n
    new_word = ""
    sentence = []

    #Each iteration produces 1 word
    for i in range(50):
        new_word = next_word(tweets,cfd,knd,grammar,last,sentence,g_n)
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


def next_word(tweets,cfd,knd,grammar,last,sentence,g_n,top_choices = 5):
    #SETTING
    avoid_copy = True
    check_length = 5

    as_tuple = tuple(last)
    as_grammar = [""]*max(0,len(sentence)-g_n) + sentence[-g_n:]
    as_grammar = tuple(as_grammar)
    new_word = None

    # Get the N most common successors for the current n last words
    best_grammar = grammar[as_grammar].most_common(2)
    choices = cfd[as_tuple].most_common(top_choices)

    if len(choices) == 0:
        # Stop if no choices are available
        # We want smoothing here!
        return ""

    if len(sentence) < 3:
        for rand in range(20):
            new_word = random.choice(choices)[0] #Get a random successor
            # Special case - only allow sentences to beging with
            # alphabetical characters or hashtags
            if len(sentence) == 0 and re.sub("#","",new_word).isalpha():
                break
    else:
        bestProb =  0;
        for c in choices:
            trigram = (last[len(last) - 2], last[len(last) - 1], c[0])
            trigramProb = knd.prob(trigram)

            # When the substring length for plagiary check is reached
            # start check the sentence.
            if len(sentence) >= check_length:
                if c[0] == "":
                    if choices[0][0] != "":
                        # Only end tweet if it is the most popular alternative
                        continue
                    if is_copy(" ".join(sentence),tweets):
                        # If the entire sentence isn't unique, don't allow to end
                        continue
                elif is_copy(" ".join((sentence+[c[0]])[-check_length:]),tweets):
                    # If the number of words given by check_length is not a substring of
                    # any tweet, allow the choice.
                    continue

            if trigramProb > bestProb and is_probable_grammar(c[0],best_grammar):
                bestProb = trigramProb
                new_word = c[0]
  
    if new_word == None:
        if top_choices < 100:
            return next_word(tweets,cfd,knd,grammar,last,sentence,g_n,top_choices*2)
        else:
            return random.choice(choices)[0]

    return new_word

def fix_tweet(tweet):

    #Remove single quotaion/paranthesis
    double = tweet.count('"')
    lpar = tweet.count('(')
    rpar = tweet.count(')')
    if double == 1: tweet = re.sub('"',"",tweet)
    if lpar == 1: tweet = re.sub(r'\(',"",tweet)
    if rpar == 1: tweet = re.sub(r'\)',"",tweet)
    #if single == 1: corr_sent = re.sub('"',"")

    # Add punctation at the end
    if tweet[-1] not in [".",",","?","!"] :
        pass#tweet += "."


    if tweet[0].isalpha() and tweet[0].lower() == tweet[0]:
        tweet = tweet[0].upper()+tweet[1:]
    tweet = re.sub(r" i "," I ",tweet)
    tweet = fix_punctation(tweet)
    return tweet

def read_file(hashtag):
    '''Reads all tweets from a file given the naming convention'''
    with open(os.getcwd()+os.path.sep+'tweet_'+hashtag) as f:
        lines = f.read().splitlines()
    return lines

if __name__ == '__main__':
    tweets = []
    while len(tweets) < 20:
        cpy,chars,tweet = generate_tweet("apple")
        if not cpy and chars > 30 and chars < 141 and tweet not in tweets:
            tweets.append(tweet)
            print(tweet)