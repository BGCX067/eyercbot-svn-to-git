#!/usr/bin/env python
# EyeRCBot 
# Version: 1.0
# Written by croxis
# As is.  If it somehow removes your root directory, it isn't my fault.

version = 1,0,0

'''
System Requirements
1) Python 2.5

Installation
See README for documentation, but in short:
1) Copy the botconfig.example.yaml file and edit your copy
3) Run "python main.py yourbotconfig.yaml"


Roadmap
Done: 0.1: Timer function prototype
Done:	 0.1.1: Eggdrop logging 
Done:	 0.1.2: Eyecron: Threaded timer function
Done: 0.2: Execute pisg automatically and by command
Done:	0.2.5: Configuration file
	0.2.6: Color compatibility in logging
Done: 0.3: Basic Google and Wikipedia search
Done:	0.3.1: Seperate Search for Civfanatics site and forum
Done:	0.3.2: Seperate Google translate
Done:	0.3.3: Script to print current time based on timezone input
		Todo: Timezone conversion
Done:	0.3.4: RSS/ATOM feed reader that can output to chat at interval
		Todo: Dict/list for more url
		Todo: Auto check for new entry at specific interval
Done: 0.4: Create user list that relies on host mask that allows user to register themselves	
Done: 	0.4.1: User can set additional information and password
Done:	0.4.2: User password is encrypted
	0.4.3: User information is automatically transferred to stats
	0.4.4: Permissions can be dynamicly set
DONE: 1.0: Talks in a lisp.  And get the logger into its own plugin
Inprog:	1.0.1: Quotes
	1.0.2: FAQ script (dict in yaml which !faq entry where entry is key and the value is returned, based on quotes)
Inprog	1.0.3: Aiml interpreter, or a wrapper for one
	1.0.4: Jabber Bridge
	1.0.5: Multiuser Dungeon, Text adventure/interactive fiction, or wrappers
	1.0.6: Mad libs, Gin Rummy
	
Optional
	Create pastebin (or alternative) dump for the java client -- does it auto by hostmask (sees the java) or manually by a special code. Pastes to http://cfc.pastebin.com/
	Civfanatics forum interface that uses rss to read a specific thread and where users can post in irc
	Full unoffical inchth google script capacity
'''

# For command line arguments and altering system paths
import sys
# External libraries are here
sys.path.append('lib')
# Scheduler from the Spyce project (http://spyce.sourceforge.net/)
import scheduler
# The long term objective is to put the ircbot functionality elsewhere and just call irclib directly
import ircbot
# For logging
import time
# For dynamic plugin loading
import glob
import imp
# For logging to process formatting
import re
# To figure out it a plugin has a certain function or not.
import inspect
# For bot configuration
import yaml
# For logging errors
import traceback

path_users = 'users/'
path_groups = 'groups/'

# Opens config from command line and enters memory
# Error control:
# If no parameter is passed, then we say boo hoo and kill program
try:
	bot_config = sys.argv[1]
except:
	print 'EyeRCbot requires a yaml configuration file.  Syntax: ./main.py botconfig.yaml'
	sys.exit(1)

# Opens bot yaml configuration file into memory
try:
	bot_config_file = open(bot_config, 'r')
except:
	print 'Terminal Error: This file does not exist or can not be opened.'
	sys.exit(1) 
stream = bot_config_file.read()
bot_config_file.close()
bot_memory = yaml.load(stream)

# Error control to make sure all needed parameters are in there
try:
	test = (bot_memory['server'], bot_memory['port'], bot_memory['nick'], bot_memory['name'], bot_memory['password'])
	test = None
except:
	print 'Terminal Error: There are errors in your configuration file.  Please check the file and try again.'
	sys.exit(1)

# Creates a list or dictionary to store the cron events
#Eyecron = []

# Subclass SingleServerIrcBot
class EyeRCbot (ircbot.SingleServerIRCBot):
	# Creates dictionary to store commands
	command = {}

	# a place to keep track of the plugins with the on_join command
	#keys are each function, values are the name of the plugins with that function
	plugins = {}
	function_list = ['on_welcome','on_ctcp','on_join','on_kick','on_mode','on_nick','on_part','on_pubmsg','on_privmsg','on_quit','on_topic']
	for key in function_list:
		plugins[key] = []

	# We are now storing the user and group dict in the class so that any plugin can access it equaly
	# For now it will be up to the plugin to read or write to disk
	user_list = {}
	group_list = {}
	
	def launch(self):
		# Load users and groups
		self.load_users()
		self.load_groups()
		# Initial scan for commands
		self.pluginScan()
		# Launching sequence
		self._connect()
		# Enters final bot launch and infinite loop
		self.runtime()
	
	# Scan the plugin directory and loads them.  (Use the code for the quote script as well)
	# Its replacement will pull command(s) from inside file, not the filename
	def pluginScan(self):
		# We flush out loaded plugins to prevent doubling up in memory
		self.command.clear()
		plugins = {}
		for key in self.function_list:
			self.plugins[key] = []
		

		for moduleSource in glob.glob ( 'plugins/*.py' ):
			name = moduleSource.replace ( '.py', '' ).replace ( '\\', '/' ).split ( '/' ) [ 1 ].upper()
			handle = open ( moduleSource )
			module = imp.load_module ( name, handle, ( 'plugins/' + moduleSource ), ( '.py', 'r', imp.PY_SOURCE ) )
			self.command [ name ] = module
			self.command[name].on_load(self.connection)
		
		#Go through the list of plugins..
		for name in self.command.keys():
			#and list all the functions the plugin has.
			functs = inspect.getmembers(self.command[name],inspect.isfunction)
			#each function is returned as a tuple (or maybe a list) 0, being the name, and 1 being the function itself
			for tuple in functs:
				for poss_functs in self.function_list:
					#since we only need the name of the function to match up, we only use the name in [0]
					if tuple[0] == poss_functs:
						#add it to our list of the applicable functions..
						self.plugins[poss_functs].append(self.command[name])
		#This can be expanded as needed with no trouble at all to any of the functions the main bot can handle.
		
		# Prints command list to console for diagnostics
		print self.command
		print self.plugins

	# Infinite runtime loop
	def runtime(self):
		# The infinite loop
		#try:
		while 1:
			# Socket data processing
			self.ircobj.process_once(0.2)
		#except Exception, e:
		#	print e
		#	print 'Terminal Error: I am quitting'
		#	sys.exit(1)

	# Connection protocol from ircbot as ircbot's implementation does not lead to what we want at this time.  
	# Will need to start customizing libraries as features become more advanced
	def _connect(self):
		"""[Internal]"""
		ircpassword = None
		if len(self.server_list[0]) > 2:
			ircpassword = self.server_list[0][2]
		try:
			self.connect(self.server_list[0][0], self.server_list[0][1], self._nickname, ircpassword, ircname=self._realname)
		except ServerConnectionError:
			print 'Error connection to server'
			return

	# Join channel when welcomed (?)
	def on_welcome (self, connection, event):
		for chan in bot_memory['channels']:
			connection.join(chan)
		# vbraun edits start here
		# if a plugin has the on_welcome function, call it.
		for plugin in self.plugins['on_welcome']:
			plugin.on_welcome(connection, event, self.channels)
		# vbraun edits end here

	# Reacts to CTCP
	def on_ctcp (self, connection, event):
		# Listen to CTCP messages for the scan password
		# If we get it, rescan
		if event.arguments()[0] == str(bot_memory['password']).upper():
			self.pluginScan()

		# vbraun edits start here
		# if a plugin has the on_ctcp function, call it.
		for plugin in self.plugins['on_ctcp']:
			plugin.on_ctcp(connection, event, self.channels)
		# vbraun edits end here

	# When someone joins the channel
	def on_join(self, connection, event):
		
		# Announces to channel that bot joined and version number
		if event.source().split('!')[0] == bot_memory['nick']:
			connection.privmsg(event.target(), 'EyeRCbot joined. Version: ' + str(version))
			
		# vbraun edits start here
		# if a plugin has the on_join function, call it.
		for plugin in self.plugins['on_join']:
			# nickname is passed for logging script
			plugin.on_join(connection, event, self.channels, self._nickname)
		# vbraun edits end here

	# When someone is kicked
	def on_kick(self, connection, event):
		# If we are kicked we will attempt to rejoin
		if event.arguments()[0] == bot_memory['nick']:
			connection.join(event.target())
		
		# vbraun edits start here
		# if a plugin has the on_kick function, call it.
		for plugin in self.plugins['on_kick']:
			print "in main file.."
			plugin.on_kick(connection, event, self.channels)
		# vbraun edits end here

	def on_mode (self, connection, event):
		
		# vbraun edits start here
		# if a plugin has the on_mode function, call it.
		for plugin in self.plugins['on_mode']:
			plugin.on_mode(connection, event, self.channels)
		# vbraun edits end here

	# Listens for nick changes and writes to log
	def on_nick (self, connection, event):

		# vbraun edits start here
		# if a plugin has the on_nick function, call it.
		for plugin in self.plugins['on_nick']:
			plugin.on_nick(connection, event, self.channels)
		# vbraun edits end here

	# Reacts to partings
	def on_part (self, connection, event):

		# vbraun edits start here
		# if a plugin has the on_part function, call it.
		for plugin in self.plugins['on_part']:
			plugin.on_part(connection, event, self.channels)
		# vbraun edits end here

	# Reacts to channel messages
	def on_pubmsg (self, connection, event):
		# Removes formatting as it inhibits commands
		text = re.compile('[\x02\x1f\x16\x0f \x03[0-9]{1,2}(,[0-9]{1,2})?]').sub('',event.arguments()[0])
		# If user says our name prefixed with a !, we react
		# We will need to check if the users plugin is installed and, if so, check if they have a - on module or their command
		if text.split()[0].startswith('!') == True:
			# This should be threaded?
			if self.command.has_key(event.arguments()[0].split()[0].upper().lstrip('!')):
				if self.command.has_key('USER'):
					# Scan for permission
					if self.command['USER'].checkPermission(connection, event) == True:
						self.command[event.arguments()[0].split()[0].upper().lstrip('!')].index (connection, event, self.channels)
					else:
						connection.privmsg(event.target(), "I can't let you use that command")
				else:
					self.command[event.arguments()[0].split()[0].upper().lstrip('!')].index (connection, event, self.channels)
			# Prints out basic help which lists commands
			# We will want to modify this to check for what plugins the user can do
			if event.arguments()[0].split()[0].upper().lstrip('!') == 'HELP':
				connection.privmsg(event.target().split('!')[0], 'EyeRCbot Version ' + ''.join(str(version)) + ' Loaded plugins: ' + ', '.join(self.command.keys()) + ' (!plugin help for more)')
				
		# vbraun edits start here
		# if a plugin has the on_pubmsg function, call it.
		for plugin in self.plugins['on_pubmsg']:
			plugin.on_pubmsg(connection, event, self.channels)
		# vbraun edits end here

	# Reacts to private messages
	def on_privmsg (self, connection, event):
		# Removes formatting as it inhibits commands
		text = re.compile('[\x02\x1f\x16\x0f \x03[0-9]{1,2}(,[0-9]{1,2})?]').sub('',event.arguments()[0])
		# If user says our name prefixed with a !, we react
		# We will need to check if the users plugin is installed and, if so, check if they have a - on module or their command
		if text.split()[0].startswith('!') == True:
			# This should be threaded?
			if self.command.has_key(event.arguments()[0].split()[0].upper().lstrip('!')):
				self.command[event.arguments()[0].split()[0].upper().lstrip('!')].index (connection, event, self.channels)
			# Prints out basic help which lists commands
			if event.arguments()[0].split()[0].upper().lstrip('!') == 'HELP':
				connection.privmsg(event.target().split('!')[0], 'EyeRCbot Version ' + ''.join(str(version)) + ' Loaded plugins: ' + ', '.join(self.command.keys()) + ' (!plugin help for more)')
				
		# vbraun edits start here
		# if a plugin has the on_privmsg function, call it.
		for plugin in self.plugins['on_privmsg']:
			plugin.on_privmsg(connection, event, self.channels)
		# vbraun edits end here

	# Reacts to clients leaving	
	def on_quit (self, connection, event):
		# vbraun edits start here
		# if a plugin has the on_quit function, call it.
		for plugin in self.plugins['on_quit']:
			plugin.on_quit(connection, event, self.channels)
		# vbraun edits end here

	# Logs topic changes
	def on_topic(self, connection, event):
		# vbraun edits start here
		# if a plugin has the on_topic function, call it.
		for plugin in self.plugins['on_topic']:
			plugin.on_topic(connection, event, self.channels)

	def load_users(self):
		self.user_list.clear()
		# We scan the user folder and load them into a dictionary
		# Issues with directories (ie .svn).  Look into os.walk?
		for userSource in glob.glob ( path_users + '*.yaml' ):
			name = userSource.replace ( '.yaml', '' ).replace ( '\\', '/' ).split ( '/' ) [ 1 ]
			user_file = open(userSource)
			stream = user_file.read()
			user_file.close()
			self.user_list[name] = yaml.load(stream)

	def load_groups(self):
		self.group_list.clear()
		# We scan the user folder and load them into a dictionary
		# Issues with directories (ie .svn).  Look into os.walk?
		for groupSource in glob.glob ( path_groups + '*.yaml' ):
			name = groupSource.replace ( '.yaml', '' ).replace ( '\\', '/' ).split ( '/' ) [ 1 ]
			group_file = open(groupSource)
			stream = group_file.read()
			group_file.close()
			self.group_list[name] = yaml.load(stream)

# Create an instance of EyeRCbotClass
bot = EyeRCbot( [(bot_memory['server'], bot_memory['port'])], bot_memory['nick'], bot_memory['name'])

# Launches Bot
try:
	bot.launch()
except:
        print "Trigger Exception, traceback info forward to log file."
        traceback.print_exc(file=open("errlog.txt","a"))
        sys.exit(1)

