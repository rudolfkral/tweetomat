from twython import Twython, TwythonError
from django.core.urlresolvers import reverse
from dateutil import parser
from tpz_core.models import Hashtag, Party, Twitter_account, Account_stats, Idol, Quote
from django.utils import timezone
from datetime import datetime, timedelta
from tpz_core.pref import get_pref
from tpz_core.lasts import get_lasts, set_lasts, get_last_idol, get_last_quote
import random
import os
import json

APP_KEY = 'hJvsClzbtUnhN0rUH9jZHg'
APP_SECRET = 'ZG1ksX6UnxBqTfqUBLQ9mOp9kItj70rFDjvNnE8'
OAUTH_TOKEN = ''
OAUTH_TOKEN_SECRET = ''
TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'tokens.json')
LOGGED = False

def load_tokens():
	json_file = open(TOKEN_FILE)
        json_dump = json.load(json_file)
	json_file.close()
	global OAUTH_TOKEN
	OAUTH_TOKEN = json_dump['OAUTH_TOKEN']
	global OAUTH_TOKEN_SECRET
	OAUTH_TOKEN_SECRET = json_dump['OAUTH_TOKEN_SECRET']

def save_tokens():
	new_tok = {}
	new_tok['OAUTH_TOKEN'] = OAUTH_TOKEN
	new_tok['OAUTH_TOKEN_SECRET'] = OAUTH_TOKEN_SECRET
	json_file = open(TOKEN_FILE, 'w')
	json.dump(new_tok, json_file)
	json_file.close()

def get_tokens():
	twit = Twython(APP_KEY, APP_SECRET)
	auth = twit.get_authentication_tokens(callback_url='http://127.0.0.1:8000/tpz/login')
	global OAUTH_TOKEN
	OAUTH_TOKEN = auth['oauth_token']
	global OAUTH_TOKEN_SECRET
	OAUTH_TOKEN_SECRET = auth['oauth_token_secret']
	return auth['auth_url']

def get_final_tokens(oauth_verifier):
	#print OAUTH_TOKEN
	#print OAUTH_TOKEN_SECRET
	twit = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
	final_step = twit.get_authorized_tokens(oauth_verifier)
	global OAUTH_TOKEN
	OAUTH_TOKEN = final_step['oauth_token']
	global OAUTH_TOKEN_SECRET
	OAUTH_TOKEN_SECRET = final_step['oauth_token_secret']
	save_tokens()
	global LOGGED
	LOGGED = True

def is_logged():
	if LOGGED:
		return True
	load_tokens()
	twit = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
	try:
		twit.verify_credentials()
		global LOGGED
		LOGGED = True
		return True
	except TwythonError:
		LOGGED = False
		return False

def post_status(new_status):
	load_tokens()
	twit = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
	twit.update_status(status=new_status)

def get_recent_tweet():
	load_tokens()
	twit = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
	result = twit.get_home_timeline(count=1)
	return result

def retweet(tid):
	load_tokens()
	twit = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
	twit.retweet(id=tid)

def unfriend_all():
	load_tokens()
	twit = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
	me = twit.verify_credentials()
	friends = twit.get_friends_ids(user_id=int(me['id']))['ids']
	for fid in friends:
		twit.destroy_friendship(user_id=int(fid))

def befriend_all(newfriends):
	load_tokens()
	twit = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
	for fid in newfriends:
		twit.create_friendship(screen_name=fid.login)

def twitter_date_to_datetime(twdate):
	return parser.parse(twdate)

def update_hashtags(chosen_party_id):
	hashtags_dates = Hashtag.objects.filter(party__pk=chosen_party_id).order_by('-last_used')[:1]
	if hashtags_dates.count() < 1:
		hashtags_last_update = timezone.now() - timedelta(weeks=2)
	else:
		hashtags_last_update = hashtags_dates[0].last_used
	#print hashtags_last_update
	hashtags = hashtags_since(hashtags_last_update)
	#print hashtags
	for htag in hashtags:
		q = Hashtag.objects.filter(name=htag, party__pk=chosen_party_id)
		if q.count() > 0:
			q[0].retweets += hashtags[htag]
			q[0].last_used = timezone.now()
			q[0].save()
		else:
			nq = Hashtag(name=htag, retweets=hashtags[htag], last_used=timezone.now(), party=Party.objects.get(pk=chosen_party_id))
			nq.save()


def hashtags_since(sdate):
	load_tokens()
	twit = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
	all_tweets = twit.get_home_timeline(count=200, include_entities=True)
	hashtag_map = {}
	for tweet in all_tweets:
		if twitter_date_to_datetime(tweet['created_at']) > sdate:
			for htag in tweet['entities']['hashtags']:
				#print htag['text']
				if htag['text'] in hashtag_map:
					hashtag_map[htag['text']] = hashtag_map[htag['text']] + 1
				else:
					hashtag_map[htag['text']] = 1
	return hashtag_map

def add_friends_of(fid):
	prim_friend = Twitter_account.objects.get(login=fid)
	our_rank = prim_friend.rank
	load_tokens()
	twit = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
	friends = twit.get_friends_list(screen_name=fid)
	while True:
		for friend_obj in friends['users']:
			friend = friend_obj['screen_name']
			existing = Twitter_account.objects.filter(login=friend)
			if existing.count() < 1:
				s = Account_stats(last_updated=timezone.now(), last_used=timezone.now())
				s.save()
				t = Twitter_account(login=friend, rank=(our_rank + 1), stats=s)
				t.save()
				for folparty in prim_friend.party.all():
					t.party.add(folparty)
				t.save()
			else:
				if existing[0].rank > (our_rank + 1):
					existing[0].rank = (our_rank + 1)
				for folparty in prim_friend.party.all():
					existing[0].party.add(folparty)
				existing[0].save()
			try:
				twit.create_friendship(screen_name=friend)
			except TwythonError:

				#print 'Already befriended ' + friend
		if friends['next_cursor'] == 0:
			break
		else:
			friends = twit.get_friends_list(screen_name=fid, cursor=friends['next_cursor'])
def post_idol():
	prefs = get_pref()
	idols_birth = Idol.objects.filter(birth_date__day=datetime.today().day, birth_date__month=datetime.today().month, party__pk=prefs['chosen_party'])
	idols_death = Idol.objects.filter(death_date__day=datetime.today().day, death_date__month=datetime.today().month, party__pk=prefs['chosen_party'])
	all_idols = idols_birth | idols_death
	if all_idols.count() < 1:
		return False
	chosen_idol = all_idols[random.randint(0, all_idols.count() - 1)]
	#print chosen_idol.long_name
	all_messages = Text_template.objects.filter(temp_type=1, party__pk=prefs['chosen_party'])
	chosen_message = all_messages[random.randint(0, all_messages.count() - 1)]
	#print chosen_message.text
	final_msg = get_idol_message(chosen_idol.short_name, chosen_idol.long_name, chosen_idol.birth_date, chosen_idol.death_date, chosen_message.text)
	#print final_msg
	try:
		post_status(final_msg)
	except TwythonError:
		return False
	newlasts = get_lasts()
	newlasts['last_idol'] = str(timezone.now())
	set_lasts(newlasts)
	return True

def post_quote():
	prefs = get_pref()
	quotes_birth = Quote.objects.filter(author__birth_date__day=datetime.today().day, author__birth_date__month=datetime.today().month, party__pk=prefs['chosen_party'])
	quotes_death = Quote.objects.filter(author__death_date__day=datetime.today().day, author__death_date__month=datetime.today().month, party__pk=prefs['chosen_party'])
	all_quotes = quotes_birth | quotes_death
	if all_quotes.count() < 1:
		return False
	chosen_quote = all_quotes[random.randint(0, all_quotes.count() - 1)]
	#print chosen_quote.text
	all_messages = Text_template.objects.filter(temp_type=0, party__pk=prefs['chosen_party'])
	chosen_message = all_messages[random.randint(0, all_messages.count() - 1)]
	#print chosen_message.text
	final_msg = get_quote_message(chosen_quote.author.short_name, chosen_quote.author.long_name, chosen_quote.year, chosen_quote.text, chosen_message.text)
	#print final_msg
	try:
		post_status(final_msg)
	except TwythonError:
		return False
	newlasts = get_lasts()
	newlasts['last_quote'] = str(timezone.now())
	set_lasts(newlasts)
	return True
