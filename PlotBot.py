
# coding: utf-8

# In[1]:


#Depenencies, initialize api and analyzer
import tweepy
import json
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import tconfig_h
import time

api = tconfig_h.auth()

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()


# ### Functions

# In[2]:


#Create list of compound sentiment scores for user
def score_list(target_user):

    sentiment_list = []
    # Loop through 25 pages of tweets (total 500 tweets)
    for x in range(25):
        # Get all tweets from target user's feed
        public_tweets = api.user_timeline(target_user, page=x)
        if len(public_tweets)==0:
            break

        for tweet in public_tweets:
            # Run Vader Analysis on each tweet
            text = tweet["text"]
            score = analyzer.polarity_scores(text)["compound"]

            sentiment_list.append(score)
    return sentiment_list


# In[3]:


def imgpath(user):
    return f"{user}_plot.png"


# In[4]:


#Plot sentiments over time, save image
def plot_sentiment(user, slist):

    td=datetime.today()
    date=f"{td.month}/{td.day}/{td.year%100}"

    x_axis = np.arange(len(slist))

    plt.figure(figsize=[10,6])

    plt.plot(x_axis,slist,alpha=.8,linewidth=.5,marker="o",mew=0,label="@"+user,)
    plt.xlabel("Tweets Ago",fontsize=13)
    plt.ylabel("Tweet Polarity",fontsize=13)
    plt.title(f"Sentiment Analysis of Tweets ({date})",fontsize=14,)

    plt.legend(loc=6,bbox_to_anchor=(1,0.5),fontsize=12)
    plt.grid(alpha=0.3)
    
    plt.savefig(imgpath(user),pad_inches=0.1,bbox_inches="tight")
    plt.show()


# In[5]:


#Tweet out saved plot
def tweet_plot(user, requester):
    text = f"New Tweet Analysis: @{user} (Requested by @{requester})"
    api.update_with_media(imgpath(user),text)


# In[6]:


#Returns viable username from beginning of a string
def get_handle(req):
    req=req.strip("@")
    ind = None
    for i in range(len(req)):
        char=req[i]
        if not (char.isalnum() or char=="_"):
            ind = i
            break
    return req[:ind]


# In[27]:


#Get a list of most recent plotbot requests
def get_latest_requests(recent_id, max_requests=10):

    # "Real Person" Filters
    min_tweets = 5
    max_tweets = 10000
    max_followers = 2500
    max_following = 2500

    req_list=[]
    # Retrieve 100 tweets
    searched_tweets = api.search("@PlotBot", count=max_requests, result_type="recent",since_id=recent_id)

    for tweet in searched_tweets["statuses"]:
        #Filter out possible bots
        if not (tweet["user"]["followers_count"] < max_followers and
            tweet["user"]["statuses_count"] > min_tweets and
            tweet["user"]["statuses_count"] < max_tweets and
            tweet["user"]["friends_count"] < max_following):
            continue

        if tweet["text"].lower().startswith("@plotbot analyze:"):
            req_text = tweet["text"].lower().replace("@plotbot analyze:","").strip(" ")
            if req_text.startswith("@"):
                target_user = get_handle(req_text)

                requester=tweet["user"]["screen_name"]
                req_id=tweet["id"]
            
                req_list.append((target_user,requester,req_id))
            else: print("Not a handle:", req_text)
        #else: print(tweet["text"])

    return req_list


# In[26]:


#Here we go!
reqs=get_latest_requests("",max_requests=20)
stale_targets = ["plotbot5","khmccurdy","uwebollraw","muffiniffum"]

while True:
    for t in reqs:
        target_user = t[0]
        requester = t[1]
        recent_id = t[2]
        if target_user in stale_targets:
            print("Stale target:", target_user)
            continue
        print("----")
        print(f"Preparing to analyze @{target_user}...")
        try:
            sl=score_list(target_user)
            print(f"Obtained scores for @{target_user}.")
        except tweepy.error.TweepError as e:
            print(e, "For username:", target_user)
            continue

        plot_sentiment(target_user,sl)
        print(f"Created sentiment plot for @{target_user}.")
        print(imgpath(target_user))
        try:
            tweet_plot(target_user,requester)
            print("Successfully tweeted!")
        except tweepy.error.TweepError as e:
            print(e)
        stale_targets.append(target_user)

    print("Done for now, see you in 5 minutes.")
    break
    time.sleep(300)
    reqs=get_latest_requests(recent_id)
