from urllib2 import urlopen
from dateutil import parser
import json

def get_datetime_from_yt(sth):
	return parser.parse(sth)

def get_latest_video(userid):
	raw_data = urlopen('http://gdata.youtube.com/feeds/api/users/%s/uploads?max-results=1&alt=json' % userid)
	json_data = json.load(raw_data)
	result = {}
	result['url'] = json_data['feed']['entry'][0]['media$group']['media$player'][0]['url']
	result['last_update'] = get_datetime_from_yt(json_data['feed']['entry'][0]['updated']['$t'])
	return result
