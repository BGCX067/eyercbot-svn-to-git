'''
Channel class
'''

class Channel(object):
	'''
	Channel object. Stores information about chanels and users.
	self.name = Name of channel
	self.bot = pointer to bot
	self.nicks = List of nicks present in channel
	self.plugins = List of plugin names that can be used in the channel.
	'''
	def __init__(self, bot,  name, plugins=[]):
		'''
		Initializes with pointer to bot and name of channel.
		'''
		self.name = name
		self.bot = bot
		self.nicks = []
		self.plugins = plugins
		self.populate()
		
	def populate(self):
		'''
		Flushes and populates user list
		'''
		self.nicks = []
		
	def addNick(self, nick):
		'''
		Adds nick
		'''
		self.nicks.append(nick.lstrip('!@+%').split('!').lower())
	
	def removeNick(self, nick):
		'''
		Removes nick
		'''
		self.nicks.remove(nick)
