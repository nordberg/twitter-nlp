import tweeter
import random

def get_split_tweets(hashtag, n):
    return [t.split() for t in tweeter.get_tweets(hashtag,n)[0]]

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
    model = {}
    for tweet in tweets:
        grams = find_ngrams(tweet,n)
        for gram,next_gram in grams:
            if gram in model:
                model[gram].append(next_gram)
            else:
                model[gram] = [next_gram]
    return model

def generate_tweet(model,n):
    text = []
    for i in range(25):
        words = len(text)
        tup = tuple([None]*max(0,n-words)+text[-n::])
        word = random.choice(model[tup])
        if word == None: break
        text.append(word)

    tweet = " ".join(text)
    return tweet

if __name__ == '__main__':
    n = 3
    tweets = get_split_tweets("football",150)
    model = create_model(tweets,n)
    for i in range(10):
        print(generate_tweet(model,n))
    

#   for gram,next_gram in model:
#       print(gram,":",next_gram)
#   print(tweets[0])
#   for z in find_ngrams(tweets[0], 3):
#       print(z)
