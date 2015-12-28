# Web bot code
# Pulls html from a given url

import urllib2

def bot(url):
	bot = urllib2.Request(url)
	bot.add_header('User-Agent','EyeRCbot')
	sock = urllib2.urlopen(bot)
	text = sock.read()
	sock.close()
	return text
