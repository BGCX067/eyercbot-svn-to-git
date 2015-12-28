# xrl plugin
# Plugin that can be called upon by user or script to shorten a url
# Uses the Metamark api
# http://metamark.net/api
'''xrl weblink shortener. !xrl http://url.com/index.html will shorted the link into something typable.'''
from urllib import urlopen, urlencode

def load(bot):
	pass

def unload(bot):
	pass

def main(bot, user, target, msg):
	if len(msg.split()) == 1:
		bot.message(user, target, __doc__)	
		return
	if msg.split()[1].upper() == 'HELP':
		bot.message(user, target, __doc__)	
		return
	if len(msg.split()) == 2:
		url = msg.split()[1]
		xrlurl = xrl_encoder(url)
	bot.message(user, target, user.split('!')[0] + "'s link compressed to: " + xrlurl)

def xrl_encoder(url):
	xrlurl = urlopen("http://metamark.net/api/rest/simple", urlencode({"long_url": url })).read()
	return xrlurl
