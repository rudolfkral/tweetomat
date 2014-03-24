from django.conf.urls import patterns, url

from tpz_core import views

urlpatterns = patterns('',
		url(r'preferences/', views.pref, name='pref'),
		url(r'post_idol/', views.post_idol, name='post_idol'),
		url(r'post_quote/', views.post_quote, name='post_quote'),
		url(r'retweet_most_recent/', views.retweet_most_recent, name='retweet_most_recent'),
		url(r'add_friends/', views.add_friends, name='add_friends'),
		url(r'tweet_hashtag/', views.tweet_hashtag, name='tweet_hashtag'),
		url(r'choose_hashtag/', views.choose_hashtag, name='choose_hashtag'),
		url(r'tweet_youtube/', views.tweet_youtube, name='tweet_youtube'),
		url(r'prepare/', views.prepare, name='prepare'),
		url(r'login/', views.login, name='login'),
		url(r'^$', views.index, name='index'),
)
