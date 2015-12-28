'''EyeRCbot protocol.'''
# For obvious reasons
from twisted.words.protocols import irc
#import irc
# For logging errors
import traceback
# For logging to process formatting
import re
import diskio
import yaml

import string

# Import Database
from Database import Database, UserDatabase,  PluginDatabase,  ChannelDatabase
from User import User
from Group import Group
from Entitys import Channel

# Subclass SingleServerIrcBot
class EyeRCbot (irc.IRCClient):
	'''Here is the bot logic.'''
	linerate = 1
	sourceURL = 'http://code.google.com/p/eyercbot'
	def __init__(self, config, version):
		self.configuration = config
		self.memory = {}
		self.memory['nick'] = config ['nick']
		self.version = version

		# A place to keep track of the plugins with various bot functions
		# Keys are each function, values are the name of the plugins with that function
		function_list = ['action','connectionMade','kickedFrom','names','signedOn',
		'joined', 'on_ctcp','userJoined','userKicked','modeChanged','userRenamed',
		'userLeft','privmsg', 'userQuit','topicUpdated']
		
		self.users = UserDatabase(self, User, 'users/')
		self.groups = Database(self, Group, 'groups/')
		self.channels = ChannelDatabase(self, Channel)
		self.plugins = PluginDatabase(self, function_list)
		self.plugins.loadAll()
		
		
	# ----------------------------- #
	# Protocol methods #
	# ----------------------------- #
	
	def connectionMade(self):
		'''Overide to allow nicks from yaml config'''
		# container for deferreds
		self._events = {}
		# container for NAME replies
		self._namreply = {}
		self._queue = [] 
		if self.performLogin:
			self.register(self.factory.configuration['nick'])
	
	# ---------------------------------- #
	# Callbacks for events #
	# --------------------------------- #
	# TODO: Add code so that function is only called if plugin is loaded for that channel?
	def signedOn (self):
		'''Called when succesfully signed on to server'''
		# Join channel when welcomed (?)
		for chan in self.channels.database:
			if chan != 'pm':
				self.join(chan)
		# if a plugin has the signedOn function, call it.
		for plugin in self.plugins.function['signedOn']:
			plugin.signedOn(self)
	
#	def joined(self, channel):
#		'''
#		Called when bot joins a channel. We use a pached library and defers to populate channel.
#		'''	
#		def checkNames(defer):
#			self.channels.database[channel].nicks = defer[channel]
#			for nick in self.channels.database[channel].nicks:
#				i = self.channels.database[channel].nicks.index(nick)
#				self.channels.database[channel].nicks[i] = nick.lstrip('!@+%')
#		defered = self.names(channel)
#		defered.addCallback(checkNames) 
#		'''Called when bot joins a channel'''
#		self.msg(channel, 'EyeRCbot Version: ' + str(self.version))
#		# If a plugin has joined function, call it
#		for plugin in self.plugins.function['joined']:
#			plugin.joined(self, channel.lower())

	def privmsg(self, user, target, msg):
		'''Called when bot receives public or private messages'''
		if self.configuration['isNew'] and msg.split()[0].startswith('password') :
			self.newuser(user, msg)
		# If a plugin has privmsg function, call it
		for plugin in self.plugins.function['privmsg']:
			plugin.privmsg(self, user, target, msg)
		# Removes formatting as it inhibits commands
		text = re.compile('[\x02\x1f\x16\x0f \x03[0-9]{1,2}(,[0-9]{1,2})?]').sub('',msg).lower()
		# Bug fix -- empty line causes crash, so we just skip it
		if text.split() == []:
			return None
		# If user says first word a !, we react
		# We will need to check if the users plugin is installed and, if so, check their permissions
		if text.startswith('!'):
			try:
				# TODO: This should be threaded?
				# TODO: Remove !command from string before passing?
				# TODO: Command aliases
				if target.lower() == self.memory['nick'].lower():  target = 'pm'
				# Channel is lowered due to case sensitiviy here, but not in irc
				if text.split()[0].lstrip('!') in self.plugins.commands and text.split()[0].lstrip('!') in self.channels.database[target.lower()].plugins:
					# Scan for permission
					if self.users.checkPermission(user, msg):
						self.plugins.commands[text.split()[0].lstrip('!')].main (self, user, target, msg)
					else:
						self.message(user, target,  "I can't let you use that command")
			except:
				print "Trigger Exception, traceback info forward to log file."
				self.message(user, target,  "There has been an error. Diagnostics written to errlog.txt.  Please report this bug and upload this file to: http://code.google.com/p/eyercbot/issues/list")
				traceback.print_exc(file=open("errlog.txt","a"))

	def message(self, user, target, msg):
		'''Message logic to determine how to send response based on query (prv vs pub)
		Use msg() or notice() to overide this behavior.'''
		if target == self.memory['nick']:
			# Get by pm, respond by pm
			self.msg(user.split('!')[0], msg)
		else:
			# Get by public, respond by public
			self.msg(target, msg)
	
#	def irc_JOIN(self, prefix, params):
#		"""
#		Called when a user joins a channel.
#		"""
#		nick = string.split(prefix,'!')[0]
#		channel = params[-1]
#		joinSuccessful = self._events['JOIN'][channel.lower()]
#		if nick == self.nickname:
#			self.joined(channel)
#		else:
#			self.userJoined(prefix, channel)
#		# yet the callback has always nick, channel because it's hard
#		# to write callbacks that have to react on both possibilities
#		joinSuccessful.callback((nick, channel))
#	
	def userJoined(self, user, channel):
		'''
		Call back when someone joins the channel.
		Logs nick to channel database.
		'''
		self.channels.database[channel.lower()].addNick(user)
		# if a plugin has the on_join function, call it.
		for plugin in self.plugins.function['userJoined']:
			plugin.userJoined(self, user, channel)

	def irc_PART(self, prefix, params):
		nick = string.split(prefix,'!')[0]
		channel = params[0]
		if nick == self.nickname:
			self.left(channel)
		else:
			self.userLeft(prefix, channel)

	def userLeft (self, user, channel):
		'''
		Callback for user leaving.
		Removes user from channel.
		'''
		self.channels.database[channel].removeNick(user.split('!')[0])	
		# if a plugin has the on_part function, call it.
		for plugin in self.plugins.function['userLeft']:
			plugin.userLeft(self, user, channel)

	def irc_QUIT(self, prefix, params):
		nick = string.split(prefix,'!')[0]
		self.userQuit(prefix, params[0])

	# Reacts to clients leaving	
	def userQuit(self, user, quitMessage):
		'''
		Callback for clients who quit.
		Removes user from all channels.
		'''
		self.channels.userQuit(user.split('!')[0])
		# if a plugin has the on_quit function, call it.
		for plugin in self.plugins.function['userQuit']:
			plugin.userQuit(self, user, quitMessage)
	
	def userKicked(self, kickee, channel, kicker, message):
		'''
		Callback when someone is kicked.
		Removes user form channel database.'''
		self.channels.database[channel].removeNick(kickee.split('!')[0])
		# if a plugin has the on_kick function, call it.
		for plugin in self.plugins.function['userKicked']:
			plugin.userKicked(self, kickee, channel, kicker, message)
	
	# When I see a user perform an action
	def action(self, user, channel, data):
		# if a plugin has the on_kick function, call it.
		for plugin in self.plugins.function['action']:
			plugin.action(self, user, channel, data)
	
	# On topic changes (and first join channel)
	def topicUpdated(self, user, channel, newTopic):
		# if a plugin has the on_topic function, call it.
		for plugin in self.plugins.function['topicUpdated']:
			plugin.topicUpdated(self, user, channel, newTopic)
	
	# On other user nick changes
	def userRenamed(self, oldname, newname):
		'''
		Callback when other users rename themselvs.
		Changes nick in database.
		Plugins are called before change in database
		'''
		# if a plugin has the on_nick function, call it.
		for plugin in self.plugins.function['userRenamed']:
			plugin.userRenamed(self, oldname, newname)
		self.channels.userRenamed(oldname.split('!')[0], newname.split('!')[0])
	
	#On mode changes
	def modeChanged(self, user, channel, set, modes, args):
		'''user	The user and hostmask which instigated this change. (type: str )
		channel	The channel for which the modes are changing. (type: str )
		set	true if the mode is being added, false if it is being removed. (type: bool or int )
		modes	The mode or modes which are being changed. (type: str )
		args	Any additional information required for the mode change. (type: tuple )'''
		# On user op: LogicSequence!~LogicSequ@LogicSequence.Users.irc-chat.net #civfanatics True o ('TwistedEye',)
		# if a plugin has the on_mode function, call it.
		for plugin in self.plugins.function['modeChanged']:
			plugin.modeChanged(self, user, channel, set, modes, args)
	
	# When I am kicked
	def kickedFrom(self, channel, kicker, message):
		# If we are kicked we will attempt to rejoin
		self.join(channel)
	
	def quit(self, message=''):
		'''Clean shutdown of myself. Overides twisted library'''
		for chan in self.channels.database:
			self.msg(chan, 'Bot is shutting down. Saving database and memory.')
		self.users.saveAll()
		self.groups.saveAll()
		self.saveConfig()
		self.saveMemory()
		self.sendLine("QUIT :%s" % message)
		self.factory.halt()
	
	# -------------------------------- #
	# Application methods #
	# TODO: Move these?  #
	# -------------------------------- #
	
	def newuser(self, user, msg):
		'''First user to PM their password will be registered as owner'''
		self.users.makeEntry(user.split('!')[0])
		self.users.database[user.split('!')[0]].register(user, msg.split()[1], 'owner')
		# We now write the new user file
		self.users.save(user.split('!')[0])
		self.configuration['isNew'] = False
		self.saveMemory()
		self.saveConfig()
		self.users.load(user.split('!')[0])
		self.msg(user.split('!')[0], 'You have been registered as my owner.')

	
	def saveConfig(self):
		stream = file(self.configuration['nick']  + '.yaml', 'w')
		yaml.dump(self.configuration, stream)
		stream.close()
	
	# Bot will save its memory in a yaml file for backup
	def saveMemory(self):
		stream = file('memory/' + self.configuration['nick'] +'.yaml', 'w')
		yaml.dump_all([self.memory,  self.users,  self.groups], stream)
		stream.close()
