import results
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
results = results.answers

human_tweets = [t for t in results if t[1][0]]
comp_tweets = [t for t in results if not t[1][0]]

hashtags = {}
for r in results:
	hashtag = r[1][1]
	if hashtags.get(hashtag):
		hashtags[hashtag].append(r)
	else:
		hashtags[hashtag] = [r]

hashtags_order = hashtags.keys()
sorted(hashtags_order)

values = []
total = [0,0,0,0]

for h in hashtags_order:
	human = [t[0] for t in hashtags[h] if t[1][0]]
	comp = [not t[0] for t in hashtags[h] if not t[1][0]]
	row = [human.count(True),comp.count(True),human.count(False),comp.count(False)]
	values.append(row)
	total = [t+v for t,v in zip(total,row)]

for column in values:
	c_tot = column[1]+column[3]
	h_tot = column[0]+column[2]
	column[0]/=h_tot
	column[1]/=c_tot
	column[2]/=h_tot
	column[3]/=c_tot

total[0] /= len(human_tweets)
total[1] /= len(comp_tweets)
total[2] /= len(human_tweets)
total[3] /= len(comp_tweets)

error_total = pd.DataFrame(np.array([total]),columns=['C Human','C AI','E Human','E AI'])
errors = pd.DataFrame(np.array([v[2:] for v in values]),columns=['AI guess on Human (%)','Human guess on AI (%)'],index=hashtags_order)
error_plot = errors.plot(kind='bar',color = ['b','g','grey','r'])
error_plot.plot([-1, 10], [total[2]]*2, color='b', linestyle='-', linewidth=2)
error_plot.plot([-1, 10], [total[3]]*2, color='g', linestyle='-', linewidth=2)
print(errors)
print (error_total)
plt.show()
