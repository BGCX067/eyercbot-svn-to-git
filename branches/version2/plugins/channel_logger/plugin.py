# Channel Logging Plugin
# Logs the events in the channel in eggdrop format
# vbraun I love you
'''Channel Logging Plugin.  No commands.'''

#import EyeRClib.scheduler as scheduler
from lib.Eyecron import Task
import time
import re
import yaml

# ---------------------
# Configuration
config_file = open('plugins/channel_logger/config.yaml',  'r')
stream = config_file.read()
config_file.close()
channels = yaml.load(stream)
# ---------------------

def load(bot):
	# Adds the midnight log to the Eyecron scheduler
	#scheduler.schedule_daily(bot, 00, 00, midnight, once=False)
	midnightTask = Task('Channel Log Midnight Timestamp', '00:00:00', True,  midnight,  bot)
	pass

def unload(bot):
	pass

def main(bot, user, target, msg):
	bot.message(user, target, __doc__)

# Midnight line entry
def midnight(bot):
	for chan in bot.memory['channels']:
		line = time.strftime('--- %a %b %d %Y', time.gmtime())
		eggLog(line, chan)
	
def eggLog(content, channel):
	'''Write the string to the proper log file.'''
	# IRC chan not case sensitive, we may want to lowercase if we still get odd capitalizations
	if channel not in channels:
		return
	eggLogFile = open(channels[channel] + channel.split('#')[1].lower() + time.strftime('.log.%Y%m%d', time.gmtime()), 'a')	
	timeStamp = time.strftime('[%H:%M]', time.gmtime())
	#line = timeStamp + ' ' + str(re.compile('[\x02]').sub('^B', content))
	line = timeStamp + ' ' + content
	#print line
	eggLogFile.write (line + '\n')
	eggLogFile.close()


def userJoined(self, user, channel):
	'''When someone joins the channel, log'''
	if user.split('!')[0] == self.memory['nick']:
		line = self.memory['nick'] + ' joined ' + channel + '.'
	else:
		line = user.split('!')[0] + ' (' + user.split('!')[1] + ') joined ' + channel + '.'
	eggLog(line, channel)


def userKicked(self, kickee, channel, kicker, message):
	'''Reacts to kicks, logs it'''
	line = kickee + ' kicked from ' + channel + ' by ' + kicker + ': ' + message
	eggLog(line, channel)

def modeChanged(self, user, channel, set, modes, args):
	# Listens for a mode change then writes to log
	if set:
		modes = '+' + modes
	else:
		modes = '-' + modes
	try:
		line = channel + ": mode change '" + modes + ' ' + args + "' by " + user
	except:
		line = channel + ": mode change '" + modes + " ' by " + user
	eggLog(line, channel)

def userRenamed(self, oldname, newname):
	'''Listens for nick changes, then writes to log.'''
	# We do this hack to pass to logger as I can't think of another way of passing the channel name
	for chan in channels:
		if oldname.split('!')[0]  in self.channels.database[chan].nicks:
			eggLog('Nick change: ' + oldname + ' -> ' + newname, chan)


def userLeft (self, user, channel):
	'''Reacts to partings, logs
	'''
	# TODO: Enhance library so we can pass leave message as well
	# Logs the parting
	#try:
		#line = user.split('!')[0] + ' (' + user.split('!')[1] + ') left ' + channel + ' (' + event.arguments()[0] + ').'
	#except:
	line = user.split('!')[0] + ' (' + user.split('!')[1] + ') left ' + channel + '.'
	eggLog(line, channel)
		

def privmsg(self, user, target, text):
	'''Channel text, write to log!'''
	eggLog('<' + user.split ('!')[0] + '> ' + text, target)

def userQuit(self, user, quitMessage):
	'''Reacts to partings, logs them
	'''
	for chan in channels:
		if user.split('!')[0] in self.channels.database[chan].nicks:
			eggLog(user.split('!')[0] + ' (' + user.split('!')[1] + ') left irc: ' + quitMessage, chan)

# Logs topic changes
def topicUpdated(self, user, channel, newTopic):
	'''# On topic changes (and first join channel)'''
	eggLog('Topic changed on ' + channel + ' by ' + user.strip('~') + ': ' + newTopic, channel)

def action(self, user, channel, data):
	'''If a /me action is done it is written to log'''
	line = 'Action: ' + user.split('!')[0] + ' ' + data
	eggLog(line, channel)
