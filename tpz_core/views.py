from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from dateutil import parser
import random
from django.db.models import Q
from tpz_core.forms.pref import PrefForm
from tpz_core.forms.hashtag import HashtagForm
from tpz_core.models import Party, Idol, Text_template, Quote, Twitter_account, Hashtag, Youtube_account, Account_stats
from tpz_core.pref import get_pref, set_pref
from tpz_core.twitter import get_tokens, get_final_tokens, is_logged, post_status, get_recent_tweet, retweet, unfriend_all, befriend_all, hashtags_since, update_hashtags, add_friends_of
from tpz_core.regexes import get_idol_message, get_quote_message
from tpz_core.youtube import get_latest_video
from tpz_core.lasts import get_lasts, set_lasts, get_last_idol, get_last_quote
from twython import TwythonError

chosen_hashtag = ''

# Create your views here.

def pref(request):
	if request.method == 'POST':
		form = PrefForm(request.POST)
		if form.is_valid():
			new_pref = {}
			new_pref['chosen_party']=form.cleaned_data['chosen_party'].pk
			new_pref['memoriam_interval']=form.cleaned_data['memoriam_interval']
			new_pref['quote_interval']=form.cleaned_data['quote_interval']
			set_pref(new_pref)
			return render(request, 'tpz_core/index.html', {'prepared': False, 'prefChanged': True})
	else:
		old_pref = get_pref()
		form = PrefForm(initial={
			'chosen_party': int(old_pref['chosen_party']),
			'memoriam_interval': int(old_pref['memoriam_interval']),
			'quote_interval': int(old_pref['quote_interval']),
			})

	return render(request, 'tpz_core/pref.html', {
		'form': form,
	})

def login(request):
	if request.GET.has_key('oauth_verifier'):
		oauth_verifier = request.GET['oauth_verifier']
		get_final_tokens(oauth_verifier)
		return HttpResponseRedirect(reverse('tpz_core:index'))
	else:
		return HttpResponseRedirect(get_tokens())

def post_idol(request):
	prefs = get_pref()
	idols_birth = Idol.objects.filter(birth_date__day=datetime.today().day, birth_date__month=datetime.today().month, party__pk=prefs['chosen_party'])
	idols_death = Idol.objects.filter(death_date__day=datetime.today().day, death_date__month=datetime.today().month, party__pk=prefs['chosen_party'])
	all_idols = idols_birth | idols_death
	if all_idols.count() < 1:
		return render(request, 'tpz_core/index.html', { 'noidol': True })
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
		return render(request, 'tpz_core/index.html', { 'error': True })
	newlasts = get_lasts()
	newlasts['last_idol'] = str(timezone.now())
	set_lasts(newlasts)
	return render(request, 'tpz_core/index.html', {'post_idol': final_msg})
	#return HttpResponseRedirect(reverse('tpz_core:index'))

def post_quote(request):
	prefs = get_pref()
	quotes_birth = Quote.objects.filter(author__birth_date__day=datetime.today().day, author__birth_date__month=datetime.today().month, party__pk=prefs['chosen_party'])
	quotes_death = Quote.objects.filter(author__death_date__day=datetime.today().day, author__death_date__month=datetime.today().month, party__pk=prefs['chosen_party'])
	all_quotes = quotes_birth | quotes_death
	if all_quotes.count() < 1:
		return render(request, 'tpz_core/index.html', { 'noquote': True})
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
		return render(request, 'tpz_core/index.html', { 'error': True })
	newlasts = get_lasts()
	newlasts['last_quote'] = str(timezone.now())
	set_lasts(newlasts)
	return render(request, 'tpz_core/index.html', {'post_quote': final_msg})
	#return HttpResponseRedirect(reverse('tpz_core:index'))

def retweet_most_recent(request):
	try:
		recent_tweet = get_recent_tweet()[0]
		#print recent_tweet['text']
		retweet(int(recent_tweet['id']))
	except TwythonError:
		return render(request, 'tpz_core/index.html', { 'error': True })
	return render(request, 'tpz_core/index.html', {'retweet': recent_tweet['text']})
	#return HttpResponseRedirect(reverse('tpz_core:index'))

def prepare(request):
	try:
		unfriend_all()
		prefs = get_pref()
		newfriends = Twitter_account.objects.filter(party__pk=prefs['chosen_party'])
		befriend_all(newfriends)	
	except TwythonError:
		return render(request, 'tpz_core/index.html', {'error': True})
	return render(request, 'tpz_core/index.html', {'prepared': True, 'prefChanged': False})

def tweet_hashtag(request):
	if request.method == 'POST':
		form = HashtagForm(request.POST)
		if form.is_valid():
			new_status = form.cleaned_data['text'] + ' #' + chosen_hashtag
			q = Hashtag.objects.get(name=chosen_hashtag)
			q.last_used = timezone.now()
			q.save()
			#print new_status
			try:
				post_status(new_status)
			except TwythonError:
				return render(request, 'tpz_core/index.html', {'error': True})
			return render(request, 'tpz_core/index.html', {'hashtag': new_status})
			#return HttpResponseRedirect(reverse('tpz_core:index'))
	else:
		form = HashtagForm()
		global chosen_hashtag
		if 'chosen' in request.GET:
			chosen_hashtag = request.GET['chosen']
		else:
			prefs = get_pref()
			try:
				update_hashtags(prefs['chosen_party'])
			except TwythonError:
				return render(request, 'tpz_core/index.html', {'error': True})
			chosen_hashtag = (Hashtag.objects.filter(party__pk=prefs['chosen_party']).order_by('-retweets', '-last_used')[:1])[0].name

	return render(request, 'tpz_core/hashtag.html', {
		'form': form,
		'htag': chosen_hashtag
	})

def choose_hashtag(request):
	prefs = get_pref()
	try:
		update_hashtags(prefs['chosen_party'])
	except TwythonError:
		return render(request, 'tpz_core/index.html', {'error': True})
	return render(request, 'tpz_core/hashtags.html', {
		'hashtag_list': Hashtag.objects.filter(party__pk=prefs['chosen_party']).order_by('-retweets', '-last_used')
	})

def add_friends(request):
	if 'chosen' not in request.GET:
		prefs = get_pref()
		try:
			update_hashtags(prefs['chosen_party'])
		except TwythonError:
			return render(request, 'tpz_core/index.html', {'error': True})
		return render(request, 'tpz_core/friends.html', {
			'friends_list': Twitter_account.objects.filter(party__pk=prefs['chosen_party']).order_by('rank')
		})
	else:
		try:
			friends = add_friends_of(request.GET['chosen'])
		except TwythonError:
			return render(request, 'tpz_core/index.html', { 'error': True})
		return render(request, 'tpz_core/index.html', {'added_friends': request.GET['chosen']})
		#return HttpResponseRedirect(reverse('tpz_core:index'))


def tweet_youtube(request):
	prefs = get_pref()
	our_gurus = Youtube_account.objects.filter(party__pk=prefs['chosen_party'])
	for guru in our_gurus:
		#print guru.login
		latest_vid = get_latest_video(guru.login)
		guru.stats.last_updated = latest_vid['last_update']
		#print str(latest_vid['last_update'])
	chosen_account = (Youtube_account.objects.filter(party__pk=prefs['chosen_party']).order_by('stats__last_used', '-stats__last_updated')[:1])[0]
	latest_vid = get_latest_video(chosen_account.login)
	#print latest_vid['url']
	try:
		post_status(latest_vid['url'])
	except TwythonError:
		return render(request, 'tpz_core/index.html', {'error': True})
	return render(request, 'tpz_core/index.html', {'youtube': latest_vid['url']})
	#return HttpResponseRedirect(reverse('tpz_core:index'))

def index(request):
	if is_logged():
		#print 'Performing check.'
		prefs = get_pref()
		if timezone.now() > (parser.parse(get_last_idol()) + timedelta(hours=prefs['memoriam_interval'])):
			#print 'Tweeting about idol.'
			return post_idol(request)
		if timezone.now() > (parser.parse(get_last_quote()) + timedelta(hours=prefs['quote_interval'])):
			#print 'Tweeting a quote.'
			return post_quote(request)

		return render(request, 'tpz_core/index.html', {'prepared': False, 'prefChanged': False})
	else:
		return login(request)

