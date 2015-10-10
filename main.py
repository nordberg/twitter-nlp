import tweeter

def get_split_tweets(hashtag, n):
	return [t.split() for t in tweeter.get_tweets(hashtag,n)]

def find_ngrams(input_list,n):
  bigram_list = []
  for i in range(n):
    bigram_list += [([None]*(n-i) + input_list[0:max(0,i)],input_list[i])]
  for i in range(n,len(input_list)):
    bigram_list += [(input_list[i-n:i],input_list[i])]
  for i in range(n):
    bigram_list += [(input_list[len(input_list)-n:len(input_list)-i]+[None]*i,None)]
  return bigram_list

if __name__ == '__main__':
	tweets = get_split_tweets("KD riksdag",10)
	print(tweets[0])
	for z in find_ngrams(tweets[0], 3):
		print(z)