'''EyeRCbot protocol.'''
# For obvious reasons
#from twisted.words.protocols import irc
import irc
# For logging errors
import traceback
# For logging to process formatting
import re
# For dynamic plugin loading
import glob
import imp
# To figure out it a plugin has a certain function or not.
import inspect
import diskio
import yaml

version = 1, 9, 1, 0

# Subclass SingleServerIrcBot
class EyeRCbot (irc.IRCClient):
	'''Here is the bot logic.'''
	linerate = 1
	sourceURL = 'http://code.google.com/p/eyercbot'
	def __init__(self, memory):
		self.memory = memory
		self.plugins = {}
		self.commands = {}
		# A place to keep track of the plugins with various bot functions
		# Keys are each function, values are the name of the plugins with that function
		self.function_list = ['action','connectionMade','kickedFrom','names','signedOn',
		'joined', 'on_ctcp','userJoined','userKicked','modeChanged','userRenamed',
		'userLeft','privmsg', 'userQuit','topicUpdated']
		for key in self.function_list:
			self.plugins[key] = []
		# Initial scan for commands
		self.pluginScan()
		self.users = {}
		self.groups = {}
		diskio.load_users(self)
		diskio.load_groups(self)
		self.version = version
		
	# --------------------------- #
	# Protocol methods #
	# --------------------------- #
	
	def connectionMade(self):
		'''Overide to allow nicks from yaml config'''
		# container for deferreds
		self._events = {}
		# container for NAME replies
		self._namreply = {}
		self._queue = [] 
		if self.performLogin:
			self.register(self.factory.memory['nick'])
	
	# ---------------------------------- #
	# Callbacks for events #
	# --------------------------------- #
	# TODO: Add code so that function is only called if plugin is loaded for that channel?
	def signedOn (self):
		'''Called when succesfully signed on to server'''
		# Join channel when welcomed (?)
		for chan in self.memory['channels']:
			if chan not in self.memory['nick']:
				self.join(chan)
		# if a plugin has the signedOn function, call it.
		for plugin in self.plugins['signedOn']:
			plugin.signedOn(self)
	
	def joined(self, channel):
		'''Called when bot joins a channel'''
		self.msg(channel, 'EyeRCbot -- Twisted Edition! joined. Version: ' + str(version))
		# If a plugin has joined function, call it
		for plugin in self.plugins['joined']:
			plugin.joined(self, channel)

	def privmsg(self, user, target, msg):
		'''Called when bot receives public or private messages'''
		# FIXME: Special testing shutdown code
		if msg == 'idie':
			self.factory.halt()
			return
		if msg == 'iload':
			self.pluginScan()
			return
		if self.memory['isNew'] and msg.split()[0].startswith('password') :
			self.newuser(user, msg)
		# Removes formatting as it inhibits commands
		text = re.compile('[\x02\x1f\x16\x0f \x03[0-9]{1,2}(,[0-9]{1,2})?]').sub('',msg)
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
				print text.split()[0].lower().lstrip('!')
				print self.commands
				print self.memory['channels'][target]
				
				if text.split()[0].lower().lstrip('!') in self.commands and text.split()[0].lower().lstrip('!') in self.memory['channels'][target]['plugins']:
					print 'Command found'
					if 'user' in self.commands:
						# Scan for permission
						if self.commands['user'].checkPermission(self, user, msg) == True:
							self.commands[text.split()[0].lower().lstrip('!')].main (self, user, target, msg)
						else:
							self.message(user, target,  "I can't let you use that command")
					else:
						self.commands[text.split()[0].lower().lstrip('!')].main (self, user, target, msg)
			except:
				print "Trigger Exception, traceback info forward to log file."
				self.message(user, target,  "There has been an error. Diagnostics written to errlog.txt.  Please report this bug and upload this file to: http://code.google.com/p/eyercbot/issues/list")
				traceback.print_exc(file=open("errlog.txt","a"))
		# If a plugin has privmsg function, call it
		for plugin in self.plugins['privmsg']:
			plugin.privmsg(self, user, target, msg)
			

	def message(self, user, target, msg):
		'''Message logic to determine how to send response based on query (prv vs pub)
		Use msg() or notice() to overide this behavior.'''
		if target == self.memory['nick']:
			# Get by pm, respond by pm
			self.msg(user.split('!')[0], msg)
		else:
			# Get by public, respond by public
			self.msg(target, msg)
	
	# When someone joins the channel
	def userJoined(self, user, channel):
		# if a plugin has the on_join function, call it.
		for plugin in self.plugins['userJoined']:
			plugin.userJoined(self, user, channel)
	
	# Reacts to partings
	def userLeft (self, user, channel):
		# if a plugin has the on_part function, call it.
		for plugin in self.plugins['userLeft']:
			plugin.userLeft(self, user, channel)

	# Reacts to clients leaving	
	def userQuit(self, user, quitMessage):
		# if a plugin has the on_quit function, call it.
		for plugin in self.plugins['userQuit']:
			plugin.userQuit(self, user, quitMessage)
	
	# When someone is kicked
	def userKicked(self, kickee, channel, kicker, message):
		# if a plugin has the on_kick function, call it.
		for plugin in self.plugins['userKicked']:
			plugin.userKicked(self, kickee, channel, kicker, message)
	
	# When I see a user perform an action
	def action(self, user, channel, data):
		# if a plugin has the on_kick function, call it.
		for plugin in self.plugins['action']:
			plugin.action(self, user, channel, data)
	
	# On topic changes (and first join channel)
	def topicUpdated(self, user, channel, newTopic):
		# if a plugin has the on_topic function, call it.
		for plugin in self.plugins['topicUpdated']:
			plugin.topicUpdated(self, user, channel, newTopic)
	
	# On other user nick changes
	def userRenamed(self, oldname, newname):
		# if a plugin has the on_nick function, call it.
		for plugin in self.plugins['userRenamed']:
			plugin.userRenamed(self, oldname, newname)
	
	#On mode changes
	def modeChanged(self, user, channel, set, modes, args):
		'''user	The user and hostmask which instigated this change. (type: str )
		channel	The channel for which the modes are changing. (type: str )
		set	true if the mode is being added, false if it is being removed. (type: bool or int )
		modes	The mode or modes which are being changed. (type: str )
		args	Any additional information required for the mode change. (type: tuple )'''
		# On user op: LogicSequence!~LogicSequ@LogicSequence.Users.irc-chat.net #civfanatics True o ('TwistedEye',)
		#print user + ' ' + channel + ' ' + str(set) + ' ' + modes + ' ' + str(args)
		# if a plugin has the on_mode function, call it.
		for plugin in self.plugins['modeChanged']:
			plugin.modeChanged(self, user, channel, set, modes, args)
	
	# When I am kicked
	def kickedFrom(self, channel, kicker, message):
		# If we are kicked we will attempt to rejoin
		self.join(channel)
	
	# -------------------------------- #
	# Application methods #
	# TODO: Move these?  #
	# -------------------------------- #
	
	def newuser(self, user, msg):
		'''First user to PM their password will be registered as owner'''
		import hashlib
		import yaml
		new_user = {}
		new_user['password'] = hashlib.sha224(re.compile('[\x02\x1f\x16\x0f \x03[0-9]{1,2}(,[0-9]{1,2})?]').sub('',msg)).hexdigest()
		new_user['hostmasks'] = [user.split('!')[1],]
		new_user['name'] = user.split('!')[0]
		new_user['group'] = 'owner'
		new_user['permissions'] = {'whitelist':[], 'blacklist':[]}
		new_user['is_registered'] = True
		stream = file('users/' + user.split('!')[0] + '.yaml', 'w')
		yaml.dump(new_user, stream)
		stream.close()
		self.msg(user.split('!')[0], 'I have your password and host mask!  You are now registered as owner of this bot!')
		del new_user
		self.memory['isNew'] = False
		self.saveMemory()
		self.saveConfig()
		diskio.load_users(self)

	
	def saveConfig(self):
		stream = file(self.memory['nick']  + '.yaml', 'w')
		yaml.dump(self.memory, stream)
		stream.close()
	
	# Bot will save its memory in a yaml file for backup
	def saveMemory(self):
		stream = file('memory/' + self.memory['nick'] +'.yaml', 'w')
		yaml.dump_all([self.memory,  self.users,  self.groups], stream)
		stream.close()
	
	# Scan the plugin directory and loads them. 
	def pluginScan(self):
		# We flush out loaded plugins to prevent doubling up in memory
		# TODO: Look into transforming plugins into twisted plugins
		
		# For any plugins loaded we will run the unload command
		for command in self.commands:
			self.commands[command].unload(self)
		
		for key in self.function_list:
			self.plugins[key] = []
		self.memory['plugins'] = self.memory['selfPlugins']
		if 'plugins' not in self.memory:
			self.memory['plugins'] = []
		for chan in self.memory['channels']:
			for plug in self.memory['channels'][chan]['plugins']:
				self.memory['plugins'].append(plug)
		if self.memory['plugins'] == []:
			return
		self.memory['plugins'] = set(self.memory['plugins'])
		for plug in self.memory['plugins']:
			try:
				moduleSource = 'plugins/'+plug+'/plugin.py'
				name = moduleSource.replace ( '.py', '' ).replace ( '\\', '/' ).split ( '/' ) [ 1 ]
				handle = open ( moduleSource )
				module = imp.load_module ( name, handle, ( moduleSource ), ( '.py', 'r', imp.PY_SOURCE ) )
				self.commands [ name.lower() ] = module
				self.commands[name.lower()].load(self)
			except:
				print "I couldn't load " + plug + '. I placed a report in the errlog.txt file for you.'
				traceback.print_exc(file=open("errlog.txt","a"))
		#Go through the list of plugins..
		for name in self.commands.keys():
			#and list all the functions the plugin has.
			functs = inspect.getmembers(self.commands[name],inspect.isfunction)
			#each function is returned as a tuple (or maybe a list) 0, being the name, and 1 being the function itself
			for tuple in functs:
				for poss_functs in self.function_list:
					#since we only need the name of the function to match up, we only use the name in [0]
					if tuple[0] == poss_functs:
						#add it to our list of the applicable functions..
						self.plugins[poss_functs].append(self.commands[name])
		#This can be expanded as needed with no trouble at all to any of the functions the main bot can handle.
		
		# Prints command list to console for diagnostics
		#print self.commands

	
	'''# Reacts to CTCP
	def on_ctcp (self, connection, event):
		# Listen to CTCP messages for the scan password
		# If we get it, we do the command
		if event.arguments()[0] == str(self.memory['password']).upper():
			if event.arguments()[1].upper() == 'PLUGLOAD':
				self.pluginScan()
			if event.arguments()[1].upper() == 'MEMDUMP':
				self.saveMemory()
		# if a plugin has the on_ctcp function, call it.
		for plugin in self.plugins['on_ctcp']:
			plugin.on_ctcp(self, event)
	'''
