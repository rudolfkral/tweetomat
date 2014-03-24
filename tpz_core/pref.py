import json
import os

PREFERENCES_FILE = os.path.join(os.path.dirname(__file__), 'pref.json')

def get_pref():
	json_file = open(PREFERENCES_FILE)
	json_dump = json.load(json_file)
	json_file.close()
	return json_dump

def set_pref(new_pref):
	json_file = open(PREFERENCES_FILE, 'w')
	json.dump(new_pref, json_file)
	json_file.close()
