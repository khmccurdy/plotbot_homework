import os

#Keys from Heroku config

cons_key = os.environ.get('consumer_key')
cons_secret = os.environ.get('consumer_secret')
access_token = os.environ.get('access_token')
access_secret = os.environ.get('access_secret')

import tweepy
import json

def auth():
	# Setup Tweepy API Authentication
	auth_ = tweepy.OAuthHandler(cons_key, cons_secret)
	auth_.set_access_token(access_token, access_secret)
	api = tweepy.API(auth_, parser=tweepy.parsers.JSONParser())
	return api