import re

def get_readable_full_date(d):
	return "%02d.%02d.%02d" % (d.day, d.month, d.year)

def get_idol_message(shortname, longname, bdate, ddate, msg):
	if(len(msg) - 7 + len(longname) > 115):
		finalmsg = re.sub("@author", shortname, msg)
	else:
		finalmsg = re.sub("@author", longname, msg)
	finalmsg = re.sub("@bdate", get_readable_full_date(bdate), finalmsg)
	finalmsg = re.sub("@ddate", get_readable_full_date(ddate), finalmsg)
	return finalmsg

def get_quote_message(shortname, longname, syear, quote, msg):
	if(len(msg) - 12 + len(longname) + len(quote) > 115):
		finalmsg = re.sub("@author", shortname, msg)
	else:
		finalmsg = re.sub("@author", longname, msg)
	finalmsg = re.sub("@date", str(syear), finalmsg)
	finalmsg = re.sub("@quote", quote, finalmsg)
	return finalmsg
