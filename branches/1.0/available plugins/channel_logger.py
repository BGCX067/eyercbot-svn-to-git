# Channel Logging Plugin
# Logs the events in the channel in eggdrop format
# vbraun I love you

import sys
sys.path.append('lib')
import scheduler
import time
import re
import EyeRCbot


def on_load(connection):
	# Adds the midnight log to the Eyecron scheduler
	scheduler.schedule_daily(connection, 00, 00, midnight, once=False)

def on_unload(connection, event):
	pass

def on_index(connection, event, channels):
	connection.privmsg(event.target(), 'Channel Logging Plugin.  No commands.')


# Midnight line entry
def midnight(connection):
	for chan in EyeRCbot.bot_memory['channels']:
		print chan	
		line = time.strftime('--- %a %b %d %Y', time.gmtime())
		print line
		eggLog(line, chan)
	
def eggLog(content, channel):
	eggLogFile = open('log/' + channel.split('#')[1] + time.strftime('.log.%Y%m%d', time.gmtime()), 'a')	
	timeStamp = time.strftime('[%H:%M]', time.gmtime())
	line = timeStamp + ' ' + str(re.compile('[\x02]').sub('^B', content))
	print line
	eggLogFile.write (line + '\n')
	eggLogFile.close()


# When someone joins the channel
def on_join(connection, event, channels, botNick):
	# Writes joins to log
	if event.source().split('!')[0] == botNick:
		line = botNick + ' joined ' + event.target() + '.'
	else:
		line = event.source().split('!')[0] + ' (' + event.source().split('!')[1] + ') joined ' + event.target() + '.'
	eggLog(line, event.target())


# When someone is kicked
def on_kick(connection, event, channels):
	line = event.arguments()[0] + ' kicked from ' + event.target() + ' by ' + event.source().split('!')[0] + ': ' + event.arguments()[1]
	eggLog(line, event.target())

def on_mode (connection, event, channels):
	# Listens for a mode change then writes to log
	try:
		line = event.target() + ": mode change '" + event.arguments()[0] + ' ' + event.arguments()[1] + "' by " + event.source()
	except:
		line = event.target() + ": mode change '" + event.arguments()[0] + " ' by " + event.source()
	eggLog(line, event.target())

# Listens for nick changes and writes to log
def on_nick (connection, event, channels):
# Dictionary of channel names which will point to channel objects
# We do this hack to pass to logger as I can't think of another way of passing the channel name
# Ultimatly this information should be added into the library
#creates the channel object which allows us to collect or do things to the channel
	chan_name = channels.keys()
	for x in chan_name:
		for user_name in channels[x].users():
				if event.source().split('!')[0] == user_name:
					eggLog('Nick change: ' + event.source().split('!')[0] + ' -> ' + event.target(), x)

# Reacts to partings
def on_part (connection, event, channels):
	# Logs the parting
	try:
		line = event.source().split('!')[0] + ' (' + event.source().split('!')[1] + ') left ' + event.target() + ' (' + event.arguments()[0] + ').'
	except:
		line = event.source().split('!')[0] + ' (' + event.source().split('!')[1] + ') left ' + event.target() + '.'
	eggLog(line, event.target())
		
# Reacts to channel messages
def on_pubmsg (connection, event, channels):

	# Channel text, write to log!
	# Replaced odd bold character with ^B in log
	eggLog('<' + event.source().split ('!')[0] + '> ' + event.arguments()[0], event.target())


# Reacts to clients leaving	
def on_quit (connection, event, channels):
	chan_name = channels.keys()
	for x in chan_name:
		for user_name in channels[x].users():
				if event.source().split('!')[0] == user_name:
					eggLog(event.source().split('!')[0] + ' (' + event.source().split('!')[1] + ') left irc: ' + event.arguments()[0], x)

# Logs topic changes
def on_topic(connection, event, channels):
	eggLog('Topic changed on ' + event.target() + ' by ' + event.source().strip('~') + ': ' + event.arguments()[0], event.target())

# Reacts to CTCP
def on_ctcp (connection, event, channels):
	# If a /me action is done it is written to log
	if event.arguments()[0] == 'ACTION':
		line = 'Action: ' + event.source().split('!')[0] + ' ' + event.arguments()[1]
		eggLog(line, event.target())

