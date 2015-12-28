'''Database.  Usefull for group and user databases.'''

class Database(object):
	'''Database class which stores and manages database.
	self.databaseis the actual database
	self.path is the file path (string) to the files.  Ends with trailing slash
	self.prototype is the prototype class that populates the database.  yes it must be a class'''
	def __init__(self, bot, prototype, path):
		self.database = {}
		self.path = path
		self.prototype = prototype
		self.bot= bot
		self.loadAll()
	
	def loadAll(self):
		'''Loads all entries from path.'''
		import yaml
		import glob
		# We scan the user folder and load them into a dictionary
		# Issues with directories (ie .svn).  Look into os.walk?
		for source in glob.glob ( self.path + '*.yaml' ):
			name = source.replace ( '.yaml', '' ).replace ( '\\', '/' ).split ( '/' ) [ 1 ]
			entryFile = open(source)
			stream = entryFile.read()
			entryFile.close()
			self.database[name] = yaml.load(stream)
	
	def load(self, name):
		'''Loads an individual entry into the database. If "all" is passed then loadAll is called instead.'''
		if name.lower() == 'all':
			self.loadAll()
			return
		import yaml
		import glob
		entryFile = open(self.path + name + '.yaml')
		stream = entryFile.read()
		entryFile.close()
		self.database[name] = yaml.load(stream)
	
	def saveAll(self):
		'''Saves all database entries to file.'''
		import yaml
		for entry in self.database:
			stream = file(self.path + entry + '.yaml', 'w')
			yaml.dump(self.database[entry], stream)
			stream.close()
	
	def save(self, name):
		'''Saves an indivudal entry to file. If "all" is passed then saveAll is called instead.'''
		if name.lower() == 'all':
			self.saveAll()
			return
		import yaml
		stream = file(self.path + name + '.yaml', 'w')
		yaml.dump(self.database[name], stream)
		stream.close()
	
	def makeEntry(self, name):
		'''Checks to see if the entry exists and if not, makes it.'''
		if name.lower() not in self.database:
			self.database[name.lower()] = self.prototype(self.bot, name)
	
	def findEntry(self, name):
		'''
		Searches database for entry by name.
		Returns object pointer if found. None if not.
		'''
		if name in self.database:
			return self.database[name]
		else:
			return None

class UserDatabase(Database):
	'''Database with additional functions common for the user database.'''
	def __init__(self, bot, prototype, path):
		Database.__init__(self, bot, prototype, path)
	
	def findHostmask(self, hostmask):
		'''Finds user entry with that hostmask and returns that object, or None.'''
		for entry in self.database:
			if hostmask in self.database[entry].hostmasks:
				return self.database[entry]
		return None
	
	def getUser(self, user):
		'''
		Returns user object from database
		Search protocol:
		1) See if name exists and then verifies hostmask
		2) Scan entire database for hsotmask
		3) Returns a blank user object. The object is added to the database.'''
		userObject = None
		# Check to see if user name and hostmask match
		if user.split('!')[0] in self.database:
			if self.database[user.split('!')[0]].checkHostmask(user.split('!')[1]):
				userObject = self.database[user.split('!')[0]]
		# If not we scan the whole database for them
		if userObject == None:
			userObject = self.findHostmask(user.split('!')[1])
		# If we do not know them then we make them up
		if userObject == None:
			self.makeEntry(user)
			userObject = self.database[user]
		return userObject
	
	def checkPermission(self,  user, msg):
		'''Command to check if the user can use a command.
		1) Check to see if the user is in the user database by name, then hostmask
		2) If no user found, then we create new temporary User object
		3) Temp or real user object then processes permissions.
		'''
		userObject = self.getUser(user)
		# We hand off checking to that object and return boolian
		return userObject.checkPermission(self.bot, msg)
	
	def makeEntry(self, name):
		'''Checks to see if the entry exists and if not, makes it.'''
		if name not in self.database:
			self.database[name] = self.prototype(self.bot, name)

class PluginDatabase(object):
	'''
	Database for managing and interfacing with plugins.
	self.database = {'pluginname': <pluginPointer>}
	
	This is for command aliases
	self.commands = {'name': <plugin pointer>}
	
	self.function = {'eyercfunction': ['<list>','<of>','<plugin>']}
	'''
	def __init__(self, bot, functionList):
		'''
		Initializes three databases, stores the bot in case we need to acces anything, and the function list.
		'''
		self.database = {}
		self.commands = {}
		self.function = {}
		self.bot = bot
		self.functionList = functionList
		for funct in self.functionList:
			self.function[funct] = []
	
	def load(self, plugname):
		'''
		Identifies plugins from configuration file and loads them as modules into the database.
		Cleanup is done for plugins that are already loaded
		'''
		
		plugname = plugname.lower()
		
		# For plugins loaded we will run the unload command just to be safe.
		if plugname.lower() in self.database:
			self.database[pluginname].unload(self.bot)
		
		# Clean out the function list as needed
		for funct in self.function:
			if plugname.lower() in self.function[funct]:
				self.function[funct].remove(plugname.lower())
		
		# Remove from database and commands
		if plugname in self.database:
			del self.commands[plugname]
			try:
				for alias in self.database[plugname].alias:
					del self.commands[alias]
			except:
				pass
			del self.database[plugname]
		
		# And now we load the plugin into the database
		import imp, inspect
		
		try:
			moduleSource = 'plugins/'+plugname+'/plugin.py'
			name = moduleSource.replace ( '.py', '' ).replace ( '\\', '/' ).split ( '/' ) [ 1 ]
			handle = open ( moduleSource )
			module = imp.load_module ( name, handle, ( moduleSource ), ( '.py', 'r', imp.PY_SOURCE ) )
			
			# Populate the main database
			self.database[plugname.lower()] = module
			# Add any commands
			self.commands[plugname.lower()] = module
			# TODO: Add aliases 
			try:
				self.commands[plugname.lower()] + self.commands[plugname.lower()] + module.alias
			except:
				pass
			
			# Now we allow the plugin to load		
			self.database[plugname.lower()].load(self.bot)
			
		except:
			print "I couldn't load " + plug + '. I placed a report in the errlog.txt file for you.'
			import traceback
			traceback.print_exc(file=open("errlog.txt","a"))
		
		#Go through the list of plugins..
		for plugname in self.database.keys():
			#and list all the functions the plugin has.
			functs = inspect.getmembers(self.database[plugname],inspect.isfunction)
			#each function is returned as a tuple (or maybe a list) 0, being the name, and 1 being the function itself
			for tuple in functs:
				for poss_functs in self.functionList:
					#since we only need the name of the function to match up, we only use the name in [0]
					if tuple[0] == poss_functs:
						#add it to our list of the applicable functions..
						self.function[poss_functs].append(self.database[plugname])
	
	def loadAll(self):
		'''
		Loads all plugins in the configuration file.
		'''
		import imp
		# We run the unload command for all loaded plugins
		for plug in self.database:
			self.database[plug].unload(self.bot)
		# Then the function list
		for funct in self.functionList:
			self.function[funct] = []
		
		# Blank everything for a fresh start
		self.database = {}
		self.commands = {}
		
		# Scratch set for plugins
		plugins = set([])
		
		# Generate list from configuration
		for chan in self.bot.configuration['channels']:
			plugins.update(self.bot.configuration['channels'][chan]['plugins'])
		
		# If no plugins are loaded (why have a bot then?) we just return
		if plugins == set([]):
			return
		
		# Load plugins and populate the databases
		for plug in plugins:
			try:
				moduleSource = 'plugins/'+plug+'/plugin.py'
				name = moduleSource.replace ( '.py', '' ).replace ( '\\', '/' ).split ( '/' ) [ 1 ]
				handle = open ( moduleSource )
				module = imp.load_module ( name, handle, ( moduleSource ), ( '.py', 'r', imp.PY_SOURCE ) )
				
				# Populate the main database
				self.database[plug.lower()] = module
				# Add any commands
				self.commands[plug.lower()] = module
				# TODO: Add aliases 
				try:
					self.commands[plug.lower()] + self.commands[plug.lower()] + module.alias
				except:
					pass
				
				# Now we allow the plugin to load		
				self.database[plug.lower()].load(self.bot)
				
			except:
				print "I couldn't load " + plug + '. I placed a report in the errlog.txt file for you.'
				import traceback
				traceback.print_exc(file=open("errlog.txt","a"))
		
		import inspect
		#Go through the list of plugins..
		for plugname in self.database.keys():
			#and list all the functions the plugin has.
			functs = inspect.getmembers(self.database[plugname],inspect.isfunction)
			#each function is returned as a tuple (or maybe a list) 0, being the name, and 1 being the function itself
			for tuple in functs:
				for poss_functs in self.functionList:
					#since we only need the name of the function to match up, we only use the name in [0]
					if tuple[0] == poss_functs:
						#add it to our list of the applicable functions..
						self.function[poss_functs].append(self.database[plugname])

class ChannelDatabase(Database):
	'''
	Database class which stores and manages database.
	self.databaseis the actual database
	self.path is the file path (string) to the files.  Ends with trailing slash
	self.prototype is the prototype class that populates the database.  yes it must be a class
	
	Some inherited functions are nullified for more logical and sane operation.
	'''
	def __init__(self, bot, prototype):
		'''
		Initializes database. Population is done as the bot joins a channel
		'''
		self.database = {}
		self.prototype = prototype
		self.bot= bot
		self.loadAll()
	
	def loadAll(self):
		'''
		Flushes and Populates database from configuration file.
		'''
		self.database = {}
		for chanName in self.bot.configuration['channels']:
			self.database[chanName.lower()] = self.prototype(self.bot, chanName.lower(), self.bot.configuration['channels'][chanName]['plugins'])
	
	def load(self):
		pass
	
	def saveAll(self):
		pass
	
	def save(self):
		pass
	
	def makeEntry(self, name):
		'''Checks to see if the entry exists and if not, makes it.'''
		if name not in self.database:
			self.database[name] = self.prototype(self.bot)
	
	def findEntry(self, name):
		'''
		Searches database for entry by name.
		Returns object pointer if found. None if not.
		'''
		if name in self.database:
			return self.database[name]
		else:
			return None
	
	def userRenamed(self, oldnick, newnick):
		'''
		Scans database for renamed user, removes old nick, adds new nick.
		'''
		for chan in self.database:
			if oldnick in self.database[chan].nicks:
				self.database[chan].removeNick(oldnick)
				self.database[chan].addNick(newnick)
	
	def userQuit(self, nick):
		'''
		Removes user who quit from database
		'''
		for chan in self.database:
			if nick in self.database[chan].nicks:
				self.database[chan].removeNick(nick)
