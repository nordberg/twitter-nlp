# -*- coding: utf-8 -*-
from twython import Twython
import sys
import re

print(sys.stdout.encoding)

client_args = {
  "headers": {
    "accept-charset": "utf-8"
  }
}

APP_KEY = ''  # Customer Key here
APP_SECRET = ''
ACCESS_TOKEN = ''
ACCESS_SECRET = ''

twitter = Twython(APP_KEY, APP_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
results = twitter.search(q=u'apollosc2', count=100)
for tweet in results['statuses']:
        text = re.sub('@[A-Za-z]+', '', str(tweet['text'].encode(sys.stdout.encoding, errors='replace')))
        text = re.sub('(RT|RT:|RT :|RT  :)', '', text)
        text = re.sub('b\'', '', text)
        text = re.sub(':|\\n', '', text)
        print(text)
        print('')