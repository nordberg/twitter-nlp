import nltk
import os
import random
import sys
import re
import platform
from nltk.tag import StanfordPOSTagger

LOWER_CASE = False
HYBRID = True
if HYBRID:
    LOWER_CASE = False

#STANFORD AND JAVA SETUP
#nltk.internals.config_java('C:'+os.path.sep+'Program Files (x86)'+os.path.sep+'Java'+os.path.sep+'jre1.8.0_60'+os.path.sep+'bin')
#nltk.internals.config_java()
nltk.internals.config_java("C:\\Program Files (x86)\\Java\\jre1.8.0_60\\bin")
os.environ['JAVAHOME'] = "C:\\Program Files (x86)\\Java\\jre1.8.0_60\\bin"
path_to_model = os.getcwd()+os.path.sep+'stanford-postagger-2015-04-20'+os.path.sep+'models'+os.path.sep+'english-left3words-distsim.tagger'
path_to_jar = os.getcwd()+os.path.sep+'stanford-postagger-2015-04-20'+os.path.sep+'stanford-postagger.jar'

#nltk.internals.config_java('C:'+os.path.sep+'Program Files (x86)'+os.path.sep+'Java'+os.path.sep+'jre1.8.0_60'+os.path.sep+'bin')
#os.environ['JAVAHOME'] = 'C:'+os.path.sep+'Program Files (x86)'+os.path.sep+'Java'+os.path.sep+'jre1.8.0_60'+os.path.sep+'bin'
#path_to_model = os.getcwd()+os.path.sep+'stanford-postagger-2015-04-20'+os.path.sep+'models'+os.path.sep+'english-left3words-distsim.tagger'
#path_to_jar = os.getcwd()+os.path.sep+'stanford-postagger-2015-04-20'+os.path.sep+'stanford-postagger.jar'

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
    split_t = [t.split() for t in tweets if '\\' not in t and 'http' not in t]

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
    g_grams = []
    max_gram = 65000 # all tweets can cause java memory problem
    total = 1+int(len(merged)/max_gram)
    for i in range(total):
        print(i+1,total)
        g_grams += stanford.tag(merged[i*max_gram:(i+1)*max_gram])
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
    if LOWER_CASE or HYBRID:
        return any(tweet.lower() in t.lower() for t in database)
    else:
        return any(tweet in t for t in database)


def extra_trim(tweet):
    '''Makes small hacks on the tweets'''
  #  if(tweet[-1] == '\''):
  #      tweet = tweet[:-1]
    tweet = re.sub('\\n',' ',tweet)
    return tweet

def to_grammar(word):
    if word == '':
        return ''
    if single_grammar_cache.get(word):
        word_g = single_grammar_cache[word]
    else:
        try:
            word_g = stanford.tag(word)[1]
        except IndexError as e:
            print(e)
            return ''
        single_grammar_cache[word] = word_g
    return word_g

def white_space_puncation(tweet):
    tweet = re.sub(r"([\\,\\.\\?\\!])(\S)",r'\1 \2',tweet)
    tweet = re.sub(r"(\S)([\\,\\.\\?\\!])",r'\1 \2',tweet)
    return tweet

def fix_punctation(tweet):
    t1 = tweet
    for i in range(50):
        tweet = re.sub(r'([\S].)\s+([\\,\\.\\?\\!])',r'\1\2',tweet)
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

def get_n_gram(tweets,hashtag,n):
    if model_cache.get((hashtag,n)):
        return model_cache[(hashtag,n)]
    else:
        grams = create_model(tweets,n)
        model_cache[(hashtag,n)] = grams
        return grams

def generate_tweet(hashtag):

    # Settings
    n = 2
    g_n = 5

    # Gather the tweets
    tweets = [extra_trim(white_space_puncation(t)) for t in read_file(hashtag)]
    if LOWER_CASE: tweets = [t.lower() for t in tweets]

    # Create Grammar
    if grammar_cache.get(hashtag):
        g_grams = grammar_cache[hashtag]
    else:
        print('Creating grammar')
        g_grams = get_grammar_ngrams(tweets,g_n)
        grammar_cache[hashtag] = g_grams
        print('Grammar done')

    #Create n-gram model
    grams = get_n_gram(tweets,hashtag,n)
    gram1 = get_n_gram(tweets,hashtag,1)
    freq1 = nltk.ConditionalFreqDist(gram1)

    #3gram for smoothing
    if n != 3:
        grams3 = get_n_gram(tweets,hashtag,3)
    else:
        grams3 = grams
    
    # Create probability model
    cfd = nltk.ConditionalFreqDist(grams)
    grammar = nltk.ConditionalFreqDist(g_grams)
    fqd = nltk.FreqDist()
 
    for g in grams3:
        fqd[g[0]] += 1

    knd = nltk.probability.KneserNeyProbDist(fqd)
    sgt = nltk.probability.SimpleGoodTuringProbDist(fqd)

    # Init loop values
    last = ['']*n
    new_word = ''
    sentence = []

    #Each iteration produces 1 word
    for i in range(50):
        new_word = next_word(tweets,cfd,knd,sgt,grammar,freq1,last,sentence,n,g_n,hashtag)
        if new_word == '':
            #End of tweet was selected, abort appending
            break

        #Append to sentence and update last n-gram
        sentence.append(new_word)
        last = last[1:]
        last.append(new_word)

    sent = ' '.join(sentence)

    # Make some symbol correction
    corr_sent = fix_tweet(sent)

    #print the result
    return (is_copy(sent,tweets),len(sent),corr_sent)

def most_common(cfd, grammar, n_gram, sentence, top_choices, g_n):
    if HYBRID:
        as_tuple = tuple([l.lower() for l in n_gram])
    else:
        as_tuple = tuple(n_gram)
    as_grammar = [""]*max(0,len(sentence)-g_n) + sentence[-g_n:]
    as_grammar = tuple(as_grammar)
    
    # Get the N most common successors for the current n last words
    best_grammar = grammar[as_grammar].most_common(2)
    choices = cfd[as_tuple].most_common(top_choices)

    return choices,best_grammar

def next_word(tweets,cfd,knd,sgt, grammar,freq1,last,sentence,n,g_n,hashtag,top_choices = 5):
    #SETTING
    avoid_copy = True
    check_length = 5
    new_word = None
    using_smoothing = 'sgt' # 'sgt' = SimpleGoodTuring, 'knd' = Kneser-Ney
    wordProb = 0

    choices,best_grammar = most_common(cfd,grammar,last,sentence,top_choices,g_n)

    if len(choices) == 0:
        if len(sentence) > 2:
            if sentence[-n] in ['.',',','?','!']:
                new_gram = [""]*(n-1)+[sentence[-1]]
                choices,best_grammar = most_common(cfd,grammar,new_gram,sentence,top_choices,g_n)
                if len(choices) == 0:
                    choices,best_grammar = most_common(freq1,grammar,[sentence[-1]],sentence,top_choices,g_n)
        if len(choices) == 0:
            # Stop if no choices are available
            # We want smoothing here!
            return ""

    if len(sentence) < 3:
        for rand in range(20):
            new_word = random.choice(choices)[0] #Get a random successor
            # Special case - only allow sentences to beging with
            # alphabetical characters or hashtags
            if len(sentence) == 0 and re.sub('#','',new_word).isalpha():
                break
    else:
        bestProb =  0;
        for c in choices:
            wordProb = 0
            if using_smoothing == 'knd':
                trigram = (last[len(last) - 2], last[len(last) - 1], c[0])
                trigramProb = knd.prob(trigram)
                if trigramProb == 0:
                    trigramProb = c[1]/len(tweets)
                wordProb = trigramProb
            if using_smoothing == 'sgt':
                bigram = (last[len(last) -1], c[0])
                sgtProb = sgt.prob(bigram)
                wordProb = sgtProb

            # When the substring length for plagiary check is reached
            # start check the sentence.
            if len(sentence) >= check_length:
                if c[0] == '':
                    if choices[0][0] != '':
                        # Only end tweet if it is the most popular alternative
                        continue
                    if is_copy(' '.join(sentence),tweets):
                        # If the entire sentence isn't unique, don't allow to end
                        continue
                elif is_copy(fix_punctation(" ".join((sentence+[c[0]])[-check_length:])),tweets):
                    # If the number of words given by check_length is not a substring of
                    # any tweet, allow the choice.
                    continue
            if not is_probable_grammar(c[0],best_grammar):
                continue

            if wordProb > bestProb and random.randint(0,10) < 9:
                bestProb = wordProb
                new_word = c[0]
            elif wordProb == bestProb and random.randint(0,1) == 1:
                bestProb = wordProb
                new_word = c[0]

  
    if new_word == None:
        if top_choices < 100 and len(choices) == top_choices:
            return next_word(tweets,cfd,knd,sgt,grammar,freq1,last,sentence,n,g_n,hashtag,top_choices*2)
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
    if tweet[-1] not in ['.',',','?','!'] :
        pass#tweet += "."


    if tweet[0].isalpha() and tweet[0].lower() == tweet[0]:
        pass#tweet = tweet[0].upper()+tweet[1:]
    tweet = re.sub(r' i ',' I ',tweet)
    tweet = fix_punctation(tweet)
    return tweet

def read_file(hashtag):
    '''Reads all tweets from a file given the naming convention'''
    with open(os.getcwd()+os.path.sep+'tweet_'+hashtag) as f:
        lines = f.read().splitlines()
    return lines

def get_tweet(hashtag):
    cpy,chars,tweet = generate_tweet(hashtag)
    while cpy or chars < 30 or chars > 140:
        cpy,chars,tweet = generate_tweet(hashtag)
    return tweet

def generate_database(hashtags,filename,n):
    with open(filename, "a") as f:
        for h in hashtags:
            for h_t in fill_human_tweets(h,n):
                print("all_tweets.append("+str((True,h,h_t))+")",file=f)
            grammar_cache.clear()
            model_cache.clear()
            single_grammar_cache.clear()
            print(h)
            for i in range(n):
                print(i)
                print("all_tweets.append("+str((False,h,get_tweet(h)))+")",file=f)

def fill_human_tweets(hashtag,n):
    with open('tweet_'+hashtag) as f:
        return random.sample(f.read().splitlines(),n)

if __name__ == '__main__':
    #"Apple","coding","dude","halloween","happy",
    hashtags = ["Apple","coding","dude","halloween","happy","hockey","news","obama","random","weird"]
    generate_database(hashtags,"test_10x10_1.py",10)
    '''tweets = []
    while len(tweets) < 20:
        tweet = get_tweet("dude")
        tweets.append(tweet)
        print(tweet)'''
