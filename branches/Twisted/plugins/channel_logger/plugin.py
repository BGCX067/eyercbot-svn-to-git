# Channel Logging Plugin
# Logs the events in the channel in eggdrop format
# vbraun I love you
'''Channel Logging Plugin.  No commands.'''

#import EyeRClib.scheduler as scheduler
from EyeRClib.Eyecron import Task
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
	print line
	eggLogFile.write (line + '\n')
	eggLogFile.close()

def joined(self, channel):
	'''Called when bot joins a channel. We use a pached library and defers just for this bloody reason.'''	
	def checkNames(defer):
		self.memory['channels'][channel]['nicks'] = []
		self.memory['channels'][channel]['nicks'] = defer[channel]
		for nick in self.memory['channels'][channel]['nicks']:
			nick.lstrip('!@+%')
		print self.memory['channels']
	defered = self.names(channel)
	defered.addCallback(checkNames) 



# Loggins parsers
# For nick changes we need to store the user nicks in memory so we know who came and who left
# If needed elsewhere we can add this to the main protocol or library it out
# Depending on how advanced we need this, we may want to class the bot memory instead of dicting it
# This would save on a lot of repeated functions
# When someone joins the channel
def userJoined(self, user, channel):
	print 'User joined: ' + user
	'''When someone joins the channel log and add nick to memory'''
	if user.split('!')[0] == self.memory['nick']:
		line = self.memory['nick'] + ' joined ' + channel + '.'
	else:
		line = user.split('!')[0] + ' (' + user.split('!')[1] + ') joined ' + channel + '.'
	eggLog(line, channel)
	self.memory['channel'][channel]['nicks'].append(user.split('!')[0])

def userKicked(self, kickee, channel, kicker, message):
	'''Reacts to kicks, logs it, and removes nick from memory'''
	line = kickee + ' kicked from ' + channel + ' by ' + kicker + ': ' + message
	eggLog(line, channel)
	self.memory['channel'][channel]['nicks'].remove(kickee.split('!')[0])

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

# Listens for nick changes and writes to log
def userRenamed(self, oldname, newname):
	'''Listens for nick changes, changes it in bot memory nick tracking, then writes to log.'''
	# We do this hack to pass to logger as I can't think of another way of passing the channel name
	for chan in channels:
		if oldname.split('!')[0]  in self.memory['channels'][chan]['nicks']:
			eggLog('Nick change: ' + oldname + ' -> ' + newname, chan)
			self.memory['channels'][chan]['nicks'].remove(user.split('!')[0])
			self.memory['channels'][chan]['nicks'].append(user.split('!')[0])


def userLeft (self, user, channel):
	'''Reacts to partings, logs, and removes nick from chan memory'''
	# TODO: Enhance library so we can pass leave message as well
	self.memory['channels'][channel]['nicks'].remove(user.split('!')[0])
	# Logs the parting
	#try:
		#line = user.split('!')[0] + ' (' + user.split('!')[1] + ') left ' + channel + ' (' + event.arguments()[0] + ').'
	#except:
	line = user.split('!')[0] + ' (' + user.split('!')[1] + ') left ' + channel + '.'
	eggLog(line, event.target())
		

def privmsg(self, user, target, msg):
	'''Channel text, write to log!'''
	eggLog('<' + user.split ('!')[0] + '> ' + msg, target)

# Reacts to clients leaving	
def userQuit(self, user, quitMessage):
	'''Reacts to partings, logs them, and removes them from channel memory'''
	print user
	for chan in channels:
		if user.split('!')[0] in self.memory['channels'][chan]['nicks']:
			eggLog(user.split('!')[0] + ' (' + user.split('!')[1] + ') left irc: ' + quitMessage, chan)
			self.memory['channels'][chan]['nicks'].remove(user.split('!')[0])

# Logs topic changes
def topicUpdated(self, user, channel, newTopic):
	'''# On topic changes (and first join channel)'''
	eggLog('Topic changed on ' + channel + ' by ' + user.strip('~') + ': ' + newTopic, channel)

def action(self, user, channel, data):
	'''If a /me action is done it is written to log'''
	line = 'Action: ' + user.split('!')[0] + ' ' + data
	eggLog(line, channel)
