# Chatterbot plugin
# Interfaces with megahal (soon aiml/pyaiml as well)
# We hook into on_pubmsg and then respond from there
# MUST download megalhal on your own!
# mh_python (comes with megahal) must be installed

# ---------
# Configuration
# 
# Do we respond to !bot chat, botname first, or anything?
# responce_config = None, False, True
responce_config = False
# Path to megahal python libraries
#path_py_megahal = 'path/here'

import mh_python

def load(bot):
	mh_python.initbrain() 

def unload(bot):
	mh_python.cleanup() 

def main(bot, user, target, msg):
	query = msg.split(' ', 1)[1]
	bot.message(user, target, chatter(query))

def privmsg(bot, user, target, msg):
	if msg[0] != '!':
		mh_python.learn(msg)
	if responce_config == False and msg.split()[0] == bot.memory['nick']:
		query = msg.split(' ', 1)[1]
		bot.msg(target, chatter(query))
	if responce_config == True:
		query = msg
		bot.msg(target, chatter(query))

def chatter(query):
	return mh_python.doreply(query)

