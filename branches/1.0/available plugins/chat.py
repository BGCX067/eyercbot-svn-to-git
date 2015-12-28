# Chatterbot plugin
# Interfaces with megahal (soon aiml/pyaiml as well)
# We hook into on_pubmsg and then respond from there
# MUST download megalhal on your own and put mh_python into the lib directory!

# ---------
# Configuration
# 
# Do we respond to !bot chat, botname first, or anything?
# responce_config = None, False, True
responce_config = False
# Path to megahal python libraries
#path_py_megahal = 'path/here'

import mh_python
import EyeRCbot

def on_load(connection):
	mh_python.initbrain() 

def on_unload(connection, event):
	pass

def index(connection, event, channels):
	query = event.arguments()[0].split(' ', 1)[1]
	connection.privmsg(event.target(), chatter(query))

def on_pubmsg(connection, event, channels):
	if responce_config == False and event.arguments()[0].split()[0] == EyeRCbot.bot_memory['nick']:
		query = event.arguments()[0].split(' ', 1)[1]
		connection.privmsg(event.target(), chatter(query))
	if responce_config == True:
		query = event.arguments()[0]
		connection.privmsg(event.target(), chatter(query))

def chatter(query):
	return mh_python.doreply(query)

