# -*- coding: utf-8 -*-

from django import forms
from tpz_core.models import Party

class PrefForm(forms.Form):
	chosen_party = forms.ModelChoiceField(label=u'Wybrana opcja polityczna', queryset=Party.objects.all())
	memoriam_interval = forms.IntegerField(label=u'Wspomnienie co godzin')
	quote_interval = forms.IntegerField(label=u'Cytat co godzin')
