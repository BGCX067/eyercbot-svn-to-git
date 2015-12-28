#!/usr/bin/env python
# EyeRCBot 
# Version: 0.3.0
# Written by croxis
# As is.  If it somehow removes your root directory, it isn't my fault.

version = 0,3,0

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
	0.3.1: Seperate Search for Civfanatics site and forum
	0.3.2: Seperate Google translate
	0.3.3: Create pastebin (or alternative) dump for the java client -- does it auto by hostmask (sees the java) or manually by a special code. Pastes to http://cfc.pastebin.com/
	0.3.4: Script to print current time based on timezone input
	0.3.5: RSS/ATOM feed reader that can output to chat at interval
	0.3.6: Civfanatics forum interface that uses rss to read a specific thread and where users can post in irc	
	0.3.7: Full unoffical inchth google script capacity
0.4: Create user list that relies on host mask that allows user to register themselves
	0.4.1: User can set additional information and password
	0.4.2: User password is encrypted
	0.4.2: User information is automatically transferred to stats
0.5: Quotes
0.6: Aiml interpreter, or a wrapper for one
0.7: Jabber Bridge
0.8: Multiuser Dungeon, Text adventure/interactive fiction, or wrappers
0.9: Mad libs, Gin Rummy
1.0: Talks in a lisp.  And get the logger into its own plugin
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
# vbraun added: To figure out it a plugin has a certain function or not.
import inspect
# For bot configuration
#from xml.dom import minidom
import yaml

# Opens config from command line and enters memory
# Error control:
# If no parameter is passed, then we say boo hoo and kill program
try:
	bot_config = sys.argv[1]
except:
	print 'EyeRCbot requires an yaml configuration file.  Syntax: ./main.py botconfig.yaml'
	sys.exit(1)

# Opens bot yaml configuration file into memory
bot_config_file = open(bot_config, 'r')
stream = bot_config_file.read()
bot_config_file.close()
bot_memory = yaml.load(stream)

# Error control to make sure all needed parameters are in there
try:
	test = (bot_memory['server'], bot_memory['port'], bot_memory['nick'], bot_memory['name'], bot_memory['password'])
	test = None
except:
	print 'There are errors in your configuration file.  Please check the file and try again.'
	sys.exit(1)

# Creates a list or dictionary to store the cron events
#Eyecron = []

# Midnight line entry
def midnight(connection):
	if time.strftime('%H%M%S', time.gmtime()) == '000000':
		for chan in bot_memory['channels']:	
			line = time.strftime('--- %a %b %d %Y', time.gmtime())
			eggLog(line, event.target())
	
# This is the logging implementation. 
# Open log file and it will be appended ("a")
# Eggdrop format logs
# We pass event.target() to this to know which log to open
# on_nick does not list this, we must figure out how
def eggLog(content, channel, channelDB = 5):
	eggLogFile = open('log/' + channel.split('#')[1] + time.strftime('.log.%Y%m%d', time.gmtime()), 'a')	
	timeStamp = time.strftime('[%H:%M]', time.gmtime())
	line = timeStamp + ' ' + str(content)
	print line
	eggLogFile.write (line + '\n')
	eggLogFile.close()

# Subclass SingleServerIrcBot
class EyeRCbot (ircbot.SingleServerIRCBot):
	#print event.eventtype()# Passing this to plugins will be the only way to get the logger to work. 
	# Creates dictionary to store commands
	command = {}

	# a place to keep track of the plugins with the on_join command
	#keys are each function, values are the name of the plugins with that function
	plugins = {}
	function_list = ['on_welcome','on_ctcp','on_join','on_kick','on_mode','on_nick','on_part','on_pubmsg','on_privmsg','on_quit','on_topic']
	for key in function_list:
		plugins[key] = []

	def launch(self):
		# Initial scan for commands
		self.pluginScan()
		# Launching sequence
		self._connect()
		# Prints command list to console on startup for diagnostics
		print self.command
		# Enters final bot launch and infinite loop
		self.runtime()
	
	
	# Scan the plugin directory and loads them.  (Use the code for the quote script as well)
	# Its replacement will pull command(s) from inside file, not the filename
	def pluginScan(self):
		self.command.clear()
		for moduleSource in glob.glob ( 'plugins/*.py' ):
			name = moduleSource.replace ( '.py', '' ).replace ( '\\', '/' ).split ( '/' ) [ 1 ].upper()
			handle = open ( moduleSource )
			module = imp.load_module ( name, handle, ( 'plugins/' + moduleSource ), ( '.py', 'r', imp.PY_SOURCE ) )
			self.command [ name ] = module
			self.command[name].on_load(self.connection)

		#vbraun edits start here:
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
		# Adds the midnight log to the Eyecron scheduler
		scheduler.schedule_daily(self.connection, 0, 0, midnight, once=False)
		#scheduler.schedule(self.connection, 600, brain_save ,once=False)
		# The infinite loop
		while 1:
			# Socket data processing
			self.ircobj.process_once(0.2)

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
			plugin.on_welcome(connection, event)
		# vbraun edits end here

	# Reacts to CTCP
	def on_ctcp (self, connection, event):
		# Listen to CTCP messages for the scan password
		# If we get it, rescan
		if event.arguments()[0] == str(bot_memory['password']).upper():
			self.pluginScan()
		# If a /me action is done it is written to log
		if event.arguments()[0] == 'ACTION':
			line = 'Action: ' + event.source().split('!')[0] + ' ' + event.arguments()[1]
			eggLog(line, event.target())
			
		# vbraun edits start here
		# if a plugin has the on_join function, call it.
		for plugin in self.plugins['on_ctcp']:
			plugin.on_ctcp(connection, event)
		# vbraun edits end here

	# When someone joins the channel
	def on_join(self, connection, event):
		# Writes joins to log
		if event.source().split('!')[0] == self._nickname:
			line = self._nickname + ' joined ' + event.target() + '.'
		else:
			line = event.source().split('!')[0] + ' (' + event.source().split('!')[1] + ') joined ' + event.target() + '.'
		eggLog(line, event.target())
		# Announces to channel that bot joined and version number
		if event.source().split('!')[0] == bot_memory['nick']:
			connection.privmsg(event.target(), 'EyeRCbot joined. Version: ' + str(version))
			
		# vbraun edits start here
		# if a plugin has the on_join function, call it.
		for plugin in self.plugins['on_join']:
			plugin.on_join(connection, event)
		# vbraun edits end here

	# When someone is kicked
	def on_kick(self, connection, event):
		line = event.arguments()[0] + ' kicked from ' + event.target() + ' by ' + event.source().split('!')[0] + ': ' + event.arguments()[1]
		eggLog(line, event.target())
		
		# vbraun edits start here
		# if a plugin has the on_join function, call it.
		for plugin in self.plugins['on_kick']:
			plugin.on_kick(connection, event)
		# vbraun edits end here

	def on_mode (self, connection, event):
		# Listens for a mode change then writes to log
		try:
			line = event.target() + ": mode change '" + event.arguments()[0] + ' ' + event.arguments()[1] + "' by " + event.source()
		except:
			line = event.target() + ": mode change '" + event.arguments()[0] + " ' by " + event.source()
		eggLog(line, event.target())
		
		# vbraun edits start here
		# if a plugin has the on_join function, call it.
		for plugin in self.plugins['on_mode']:
			plugin.on_mode(connection, event)
		# vbraun edits end here

	# Listens for nick changes and writes to log
	def on_nick (self, connection, event):
	# Dictionary of channel names which will point to channel objects
	# We do this hack to pass to logger as I can't think of another way of passing the channel name
	# Ultimatly this information should be added into the library
	#creates the channel object which allows us to collect or do things to the channel
		chan_name = self.channels.keys()
		for x in chan_name:
			for user_name in self.channels[x].users():
					if event.source().split('!')[0] == user_name:
						eggLog('Nick change: ' + event.source().split('!')[0] + ' -> ' + event.target(), x)
		# vbraun edits start here
		# if a plugin has the on_join function, call it.
		for plugin in self.plugins['on_nick']:
			plugin.on_nick(connection, event, channelObject)
		# vbraun edits end here

	# Reacts to partings
	def on_part (self, connection, event):
		# Logs the parting
		try:
			line = event.source().split('!')[0] + ' (' + event.source().split('!')[1] + ') left ' + event.target() + ' (' + event.arguments()[0] + ').'
		except:
			line = event.source().split('!')[0] + ' (' + event.source().split('!')[1] + ') left ' + event.target() + '.'
		eggLog(line, event.target())
		
		# vbraun edits start here
		# if a plugin has the on_join function, call it.
		for plugin in self.plugins['on_part']:
			plugin.on_part(connection, event)
		# vbraun edits end here

	# Reacts to channel messages
	def on_pubmsg (self, connection, event):
		print event.target()
		# Removes formatting as it inhibits commands
		text = re.compile('[\x02\x1f\x16\x0f \x03[0-9]{1,2}(,[0-9]{1,2})?]').sub('',event.arguments()[0])
		# If user says our name prefixed with a !, we react
		# We will need to check if the users plugin is installed and, if so, check if they have a - on module or their command
		if text.split()[0].startswith('!') == True:
			# This should be threaded?
			if self.command.has_key(event.arguments()[0].split()[0].upper().lstrip('!')):
				self.command[event.arguments()[0].split()[0].upper().lstrip('!')].index (connection, event)
			# Prints out basic help which lists commands
			if event.arguments()[0].split()[0].upper().lstrip('!') == 'HELP':
				connection.privmsg(event.target().split('!')[0], 'EyeRCbot Version ' + ''.join(str(version)) + ' Loaded plugins: ' + ', '.join(self.command.keys()) + ' (!plugin help for more)')
				
		# Channel text, write to log!
		# Replaced odd bold character with ^B in log
		eggLog(re.compile('[\x02]').sub('^B', '<' + event.source().split ('!')[0] + '> ' + event.arguments()[0]), event.target())
			
		# Monolithic code
		# This is some hard code for my debuging purposes.
		# More often than not I need to kill the bot by pidof python then kill # :)
		# Will stop the bot by  me
		#if text.upper() == '!DIE' and source == 'Mobilecroxis' or source == 'croxis':
			#self.die('My master killed me!')
		
		# vbraun edits start here
		# if a plugin has the on_join function, call it.
		for plugin in self.plugins['on_pubmsg']:
			plugin.on_pubmsg(connection, event)
		# vbraun edits end here

	# Reacts to private messages
	def on_privmsg (self, connection, event):
		source = event.source().split('!')[0]
		text = event.arguments()[0]
		# vbraun edits start here
		# if a plugin has the on_join function, call it.
		for plugin in self.plugins['on_privmsg']:
			plugin.on_privmsg(connection, event)
		# vbraun edits end here

	# Reacts to clients leaving	
	def on_quit (self, connection, event):
		print event.target()
		eggLog(event.source().split('!')[0] + ' (' + event.source().split('!')[1] + ') left irc: ' + event.arguments()[0], event.target())
		# vbraun edits start here
		# if a plugin has the on_join function, call it.
		for plugin in self.plugins['on_quit']:
			plugin.on_quit(connection, event)
		# vbraun edits end here

	# Logs topic changes
	def on_topic(self, connection, event):
		eggLog('Topic changed on ' + event.target() + ' by ' + event.source().strip('~') + ': ' + event.arguments()[0], event.target())
		# vbraun edits start here
		# if a plugin has the on_join function, call it.
		for plugin in self.plugins['on_topic']:
			plugin.on_topic(connection, event)
		# vbraun edits end here

# Create an instance of EyeRCbotClass
bot = EyeRCbot( [(bot_memory['server'], bot_memory['port'])], bot_memory['nick'], bot_memory['name'])

# Launches Bot
bot.launch()
