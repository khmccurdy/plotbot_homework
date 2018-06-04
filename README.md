# PlotBot Twitter bot

This app deploys a Twitter bot that performs Sentiment Analysis on user-requested Twitter accounts, generating and tweeting out a graph of the account's last 500 tweets using Vader, Matplotlib, and Tweepy. 

App is currently turned off, may be activated for demonstration purposes on request.

```python
#Depenencies, initialize api and analyzer
import tweepy
import json
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import tconfig
import time

api = tconfig.auth()

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()
```

### Functions


```python
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
```


```python
def imgpath(user):
    return f"{user}_plot.png"
```


```python
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
```


```python
#Tweet out saved plot
def tweet_plot(user, requester):
    text = f"New Tweet Analysis: @{user} (Requested by @{requester})"
    api.update_with_media(imgpath(user),text)
```


```python
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
```


```python
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
```


```python
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
```

    Not a handle: twitter ceo
    Not a handle: ffusaadkfasdkfa;sdfk;
    Stale target: uwebollraw
    Stale target: khmccurdy
    Stale target: muffiniffum
    Stale target: plotbot5
    Done for now, see you in 5 minutes.
    


```python
get_latest_requests("")
```

    Not a handle: twitter ceo
    Not a handle: ffusaadkfasdkfa;sdfk;
    




    [('uwebollraw', 'khmccurdy', 977590669765099520),
     ('khmccurdy', 'khmccurdy', 976990403336351744),
     ('muffiniffum', 'khmccurdy', 976978547561480192),
     ('plotbot5', 'khmccurdy', 976973177057263617)]




```python
srch=api.search("@PlotBot", count=20, result_type="recent",since_id="")["statuses"]
[tweet["text"] for tweet in srch]
```




    ['@PlotBot Analyze: Twitter CEO',
     '@Plotbot Analyze: @UweBollRaw',
     '@plotbot analyze: @khmccurdy',
     '@PlOTboT aNalyZE: @muffiniffum, pleze.',
     '@plotbot analyze: @plotbot5',
     '@plotbot Analyze: ffusaadkfasdkfa;sdfk;',
     '@plotbot hi']


