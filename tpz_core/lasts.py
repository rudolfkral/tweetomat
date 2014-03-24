from tpz_core.models import Idol, Quote
import os
import json

LASTS_FILE = os.path.join(os.path.dirname(__file__), 'lasts.json')

def get_lasts():
	json_file = open(LASTS_FILE)
	json_dump = json.load(json_file)
	json_file.close()
	return json_dump

def set_lasts(new_lasts):
	json_file = open(LASTS_FILE, 'w')
	json.dump(new_lasts, json_file)
	json_file.close()

def get_last_idol():
	data = get_lasts()
	return data['last_idol']

def get_last_quote():
	data = get_lasts()
	return data['last_quote']
