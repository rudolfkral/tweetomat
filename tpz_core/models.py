from django.db import models

# Create your models here.

class Party(models.Model):
	name = models.CharField(max_length=30)
	description = models.CharField(max_length=255)
	def __unicode__(self):
		return self.name

class Hashtag(models.Model):
	name = models.CharField(max_length=45)
	retweets = models.IntegerField(default=0)
	last_used = models.DateTimeField()
	party = models.ForeignKey(Party)
	def __unicode__(self):
		return self.name

class Idol(models.Model):
	short_name = models.CharField(max_length=15)
	long_name = models.CharField(max_length=30)
	birth_date = models.DateTimeField()
	death_date = models.DateTimeField()
	party = models.ManyToManyField(Party)
	def __unicode__(self):
		return self.short_name

class Quote(models.Model):
	year = models.IntegerField(default=0)
	text = models.CharField(max_length=130)
	author = models.ForeignKey(Idol)
	party = models.ManyToManyField(Party)
	def __unicode__(self):
		return self.text

class Account_stats(models.Model):
	subscriptions = models.IntegerField(default=0)
	last_updated = models.DateTimeField()
	last_used = models.DateTimeField()

class Twitter_account(models.Model):
	login = models.CharField(max_length=15)
	rank = models.IntegerField(default=0)
	party = models.ManyToManyField(Party)
	stats = models.OneToOneField(Account_stats)
	def __unicode__(self):
		return self.login

class Youtube_account(models.Model):
	login = models.CharField(max_length=20)
	party = models.ManyToManyField(Party)
	stats = models.OneToOneField(Account_stats)
	def __unicode__(self):
		return self.login

class Text_template(models.Model):
	temp_type = models.IntegerField(default=0)
	text = models.CharField(max_length=255)
	party = models.ManyToManyField(Party)
	def __unicode__(self):
		return self.text
