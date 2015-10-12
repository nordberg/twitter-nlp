import nltk
import os
import random
import sys
import re

LOWER_CASE = False

def find_ngrams(input_list,n):
  ngram_list = []
  try:
      for i in range(n):
        ngram_list.append((tuple([None]*(n-i) + input_list[0:max(0,i)]),input_list[i]))
      for i in range(n,len(input_list)):
        ngram_list.append((tuple(input_list[i-n:i]),input_list[i]))
      for i in range(n):
        ngram_list.append((tuple(input_list[len(input_list)-n:len(input_list)-i]+[None]*i),None))
  except IndexError:
    return []
  return ngram_list

def create_model(tweets,n):
    split_t = [t.split() for t in tweets]
    model = []
    for tweet in split_t:
        grams = find_ngrams(tweet,n)
        model += grams
    return model

def is_copy(tweet, database):
    if LOWER_CASE:
        return any(tweet in t.lower() for t in database)
    else:
        return any(tweet in t for t in database)


def extra_trim(tweet):
    if(tweet[-1] == "'"):
        tweet = tweet[:-1]
    tweet = re.sub("\n"," ",tweet)
    return tweet

def generate_tweet(hashtag):
    avoid_copy = True
    check_length = 5
    n = 2
    tweets = [extra_trim(t) for t in read_file(hashtag)]
    if LOWER_CASE: tweets = [t.lower() for t in tweets]
    grams = create_model(tweets,n)
    cfd = nltk.ConditionalFreqDist(grams)
    last = [None]*n
    new_word = None
    sentence = []
    for i in range(50):
        as_tuple = tuple(last)
        choices = cfd[as_tuple].most_common(5)
        if len(choices) == 0:
            break

        # Tries to find a non-copying choice 20 times
        for j in range(20):
            new_word = random.choice(choices)[0]
            if new_word == None:
                if choices[0][0] == None:
                    continue
                if not is_copy(" ".join(sentence),tweets):
                    break
            elif not is_copy(" ".join((sentence+[new_word])[-check_length:]),tweets):
                break

        #End of tweet was selected, abort appending
        if new_word == None:
            break
        sentence.append(new_word)
        last = last[1:]
        last.append(new_word)

    sent = " ".join(sentence)
    corr_sent = sent
    double = corr_sent.count('"')
    lpar = corr_sent.count('(')
    rpar = corr_sent.count(')')
    #single = corr_sent.count("'")
    if double == 1: corr_sent = re.sub('"',"".corr_sent)
    if lpar == 1: corr_sent = re.sub('(',"".corr_sent)
    if rpar == 1: corr_sent = re.sub(')',"".corr_sent)
    #if single == 1: corr_sent = re.sub('"',"")
    if corr_sent[-1] not in [".",",","?","!"] :
        corr_sent += "."
    print(is_copy(sent,tweets),len(sent))
    print(sent)
    try:
        print(corr_sent)
    except:
        pass
 #   for word in cfd.conditions():
 #       print(word,cfd[word])
    #  print(generate_model(cfd, " ".split(random.choice(tweets))[0]))


def read_file(hashtag):
    with open(os.getcwd()+'\\tweet_'+hashtag) as f:
        lines = f.read().splitlines()
    return lines

for i in range(10):
    generate_tweet("weird")
    print()