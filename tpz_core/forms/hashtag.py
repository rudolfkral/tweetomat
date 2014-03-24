# -*- coding: utf-8 -*-

from django import forms

class HashtagForm(forms.Form):
	text = forms.CharField(label=u'Treść tweeta(bez hashtaga)')
