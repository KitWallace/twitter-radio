#!/usr/bin/env python3 

import time, json, re, sys
from urllib.request import urlopen
from urllib.parse import quote_plus
from email.utils import parsedate_tz


# local modules 
import speak

# todo :
# improved cleaning
# use a different tone to indicate @ and hash
# specify a voice so different channels can be distinguished

# eg  ./tweets.py from:george_szirtes

# replacements wil be expanded as new abbreviations are encountered

replacements = { "U.S." : "United States" ,"&amp;":"and","...":"etcetera"}

# RE to remove all the http links
removeLinks = re.compile('https?://(\S*)')


class twitter_json(object) :

   def __init__(self,query,pause,refresh) :
      self.query = query + " lang:en"
      self.url = "http://search.twitter.com/search.json?q="  + quote_plus(query)
      print(self.url)
      self.last = "2000-01-01T00:00:00"
      self.pause_secs = pause
      self.refresh_secs = refresh

   def refresh(self) :
      page = urlopen(self.url).read().decode("UTF8")   # fetch the JSON
      parsed_page= json.loads(page) 
      tweets = []
      for tweetj in parsed_page['results'] :
         tweet = tts_tweet(tweetj)
         if tweet.pubDate > self.last and tweet.accept() :
               tweet.clean()
               tweets.append(tweet)

      if len(tweets) > 0 :
            self.last = tweets[0].pubDate
            tweets.reverse() # to get them into chronological order

            for tweet in tweets :   
               print(">",tweet.pubDate,":",tweet.text)
               speak.say(tweet.cleanText)
               time.sleep( self.pause_secs)

      time.sleep(self.refresh_secs)

class tts_tweet(object) :
   def __init__(self,json) :
       self.text= json['text']    
       pubDate = json['created_at']
       pubDate = parsedate_tz(pubDate)
       self.pubDate = time.strftime("%Y-%m-%dT%H:%M:%S",pubDate[0:9])

   def clean(self) :
       mtext = removeLinks.sub(" ",self.text)
       mtext = mtext.replace("#"," ")
       mtext = mtext.replace("@"," ")
       mtext = mtext.replace("'","")
       mtext = speak.expand(mtext,replacements)
       self.cleanText = mtext

   def accept(self) :
       if self.text.startswith("RT") or self.text.startswith("@") :
          return False
       else : 
          return True
 
query = sys.argv[1]  # query string 
tweeter = twitter_json(query,4,20)
while True :
   tweeter.refresh()
 


