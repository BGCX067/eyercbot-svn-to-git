#!/usr/bin/env python
'''EyeRCbot.  A plugin IRC bot using the Twisted libraries.'''
# EyeRCBot 
# Version: 2.0
# Written by croxis and vbraun
# As is.  If it somehow removes your root directory, it isn't my fault.

# Version marker changes

# 1.0 -- Default
# 1.1 -- USER --> USERS
# 1.2 -- Plugin system now handles exceptions which are written to log without killing the whole bot
# 1.3 -- We now pass the bot instance to the plugins
# 1.4 -- More organized code. Bot responds in manner it was communicated in
# 2.0 -- Twisted library backend.  This is for AMAZEMENT!

version = 1, 9, 1, 0

'''
System Requirements
1) Python 2.5

Installation
See README for documentation, but in short:
1) Copy the botconfig.example.yaml file and edit your copy
3) Run "python main.py yourbotconfig.yaml"

Roadmap
	0.2.6: Color compatibility in logging
		Todo: Timezone conversion
Inprog:	0.3.4: RSS/ATOM feed reader that can output to chat at interval
		Todo: Dict/list for more url
		Todo: Auto check for new entry at specific interval
	0.4.3: User information is automatically transferred to stats
Inproog:   0.4.4: Permissions can be dynamicly set
Inprog:	1.0.1: Quotes
Inprog:	1.0.2: FAQ script (dict in yaml which !faq entry where entry is key and the value is returned, based on quotes)
Inprog:	1.0.3: Aiml interpreter, or a wrapper for one
	1.0.4: Jabber Bridge
	1.0.5: Multiuser Dungeon, Text adventure/interactive fiction, or wrappers
	1.0.6: Gin Rummy
	
Optional
	Create pastebin (or alternative) dump for the java client -- does it auto by hostmask (sees the java) or manually by a special code. Pastes to http://cfc.pastebin.com/they usuaally arnt
	Civfanatics forum interface that uses rss to read a specific thread and where users can post in irc
	Full unoffical inchth google script capacity
'''
# TODO: Transform botmem yaml into a yaml_all of all servers to load.  This will be in a list or dict


# For command line arguments and altering system paths
import sys
# Scheduler from the Spyce project (http://spyce.sourceforge.net/)
#import EyeRClib.scheduler
# For logging
import time
# For bot configuration
import yaml
# For logging errors
#import traceback

from EyeRClib.EyeRCprotocol import EyeRCbot

# We import the eyercbot library
import EyeRClib.diskio as diskio

from twisted.internet import reactor, protocol
#from twisted.application import internet, service
#from twisted.python import usage
#from zope.interface import implements
#from twisted.plugin import IPlugin
#from twisted.application.service import IServiceMaker


if sys.version_info < (2, 5, 0):
	sys.stderr.write('This program requires Python >= 2.5.0\n')
	print 'This program requires Python >= 2.5.0'
	sys.exit(-1)
# Creates a list or dictionary to store the cron events
#Eyecron = []

#class Options(usage.Options):
	#'''My attempt to make this a real twistd application.
	#This is to pass comand line parameters.'''
	#optParameters = [["config", "c", None, "configuration file"]]
	#def parseArgs(self, config_file):
		#self['config_file'] = config_file
	#def getConfigFile(self):
		#return self['config_file']

#class EyeXMPPbot:
#	pass
#class EyeCMPPbotFactory(protocol.ClientFactory):
#	pass

class EyeRCbotFactory(protocol.ClientFactory):
	'''The factory.'''
	protocol = EyeRCbot
	def __init__(self, memory):
		# Transition for putting bot memory into bot
		# We can probably find function overides to do this to allow more transparent passthough?
		self.memory = memory
		self.version = version
		# We are now storing the user and group dict in the class so that any plugin can access it equaly
		# For now it will be up to the plugin to read or write to disk
		# TODO: Make sure we have library function to save and write to disk (do we?)
		self.users = {}
		self.groups = {}
	def clientConnectionLost(self, connector, reason):
		'''If we lose connection, reconect!'''
		connector.connect()
	def buildProtocol(self, addr):
		"""Create an instance of a subclass of Protocol.

        The returned instance will handle input on an incoming server
        connection, and an attribute \"factory\" pointing to the creating
        factory.

        Override this method to alter how Protocol instances get created.

        @param addr: an object implementing L{twisted.internet.interfaces.IAddress}
        """
		p = self.protocol(self.memory)
		p.factory = self
		return p
	def halt(self):
		'''Hardcore reactor stoppage which can be refered to from the protocol or module.'''
		reactor.stop()


#if __name__ == "__main__":
#started = time.time()
path_users = 'users/'
path_groups = 'groups/'


#options = Options()
#try:
#	options.parseOptions()
#except:
#	print 'EyeRCbot requires a yaml configuration file.  Syntax: ./main.py botconfig.yaml'
#	sys.exit(1)
#bot_config = serviceMaker.returnOptions()
# Opens config from command line and enters memory
# Error control: If no parameter is passed, then we say boo hoo and kill program
#try:
#	bot_config = sys.argv[1]
#except:
#	print 'EyeRCbot requires a yaml configuration file.  Syntax: ./main.py botconfig.yaml'
#	sys.exit(1)
#bot_config = 'EyeRCalpha.yaml'
'''options = Options()

try:
	options.parseOptions() # When given no argument, parses sys.argv[1:]
except usage.UsageError, errortext:
	print '%s: %s' % (sys.argv[0], errortext)
	print '%s: Try --help for usage details.' % (sys.argv[0])
	sys.exit(1)
if options['config'] is None:
	print '--config=botconfig.yaml parameter is required.'
	sys.exit(1)
	
bot_config = options['config']
class MyServiceMaker(object):
	implements(IServiceMaker, IPlugin)
	tapname = "EyeRCbot"
	description = "Run this! It'll make your dog happy."
	options = Options
	def makeService(self, options):
		"""
		Construct a TCPServer from a factory defined in myproject.
		"""
		return internet.TCPServer(int(options["port"]), MyFactory())
	def makeMemory(self, options):
		''''''Returns the filename''''''
		return options["config"]
serviceMaker = MyServiceMaker()
bot_config = serviceMaker.makeMemory()'''


if __name__ == "__main__":
	started = time.time()
	path_users = 'users/'
	path_groups = 'groups/'

	# Opens config from command line and enters memory
	# Error control: If no parameter is passed, then we say boo hoo and kill program
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
		test = (bot_memory['server'], bot_memory['port'], bot_memory['nick'], bot_memory['name'])
		del test
	except:
		print 'Terminal Error: There are errors in your configuration file.  Please check the file and try again.'
		sys.exit(1)

	factory = EyeRCbotFactory(bot_memory)

	# Launches Bot
	try:
		reactor.connectTCP(bot_memory['server'], bot_memory['port'], factory)
		reactor.run()
	except:
		print "Trigger Exception, traceback info forward to log file."
		traceback.print_exc(file=open("errlog.txt","a"))
		sys.exit(1)

