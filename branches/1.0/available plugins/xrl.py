# xrl plugin
# Plugin that can be called upon by user or script to shorten a url
# Uses the Metamark api
# http://metamark.net/api

from urllib import urlopen, urlencode


def on_load(connection):
	pass

def on_unload(connection):
	pass

def index(connection, event,channels):
	if len(event.arguments()[0].split()) == 1:
		pass
	if len(event.arguments()[0].split()) == 2:
		url = event.arguments()[0].split()[1]
		xrlurl = xrl_encoder(connection, event, url)
	connection.privmsg(event.target(), event.arguments()[0].split()[1] + ' compressed to: ' + xrlurl)

def xrl_encoder(connection, event, url):
	xrlurl = urlopen("http://metamark.net/api/rest/simple", urlencode({"long_url": url })).read()
	return xrlurl
