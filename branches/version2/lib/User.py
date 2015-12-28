'''Class for user.'''

class User(object):
	'''User class. Takes the bot commander in case we need to referese bot data.'''
	def __init__(self, bot, nick=None, group=None):
		self.nick = nick
		self.alias = []
		self.group = group
		self.hostmasks = []
		self.registered = False
		self.password = None
		self.permissions = {'whitelist': [], 'blacklist': []}
	
	def setPassword(self, newPassword):
		'''Sets a new password for the user.'''
		import hashlib
		self.password = hashlib.sha224(newPassword).hexdigest()
	
	def checkPassword(self, password):
		'''Checks the user password and returns boolian on match.'''
		if self.password == hashlib.sha224(password).hexdigest():
			return True
		else:
			return False
	
	def checkHostmask(self, hostmask):
		'''Checks to see if the user is known by the given hostmask.'''
		if hostmask in self.hostmasks:
			return True
		else:
			return False
	
	def checkPermission(self, bot, command):
		'''Checks to see if user can exicute a specific command.  Returns boolian.
		Default permissions loaded first, overlayed by group then individual user permissions.
		Owner group automaticly returns true.
		!plugin (no parameters) can be masked with plugin.index'''
		if self.group == 'owner': return True
		
		finalWhite = self.returnWhitelist(bot)
		
		# Can the user use the plugin at all?
		plugin_name = command.split()[0].lstrip('!')
		#check for a multi word command
		try:
			plugin_command_name =command.split()[0].lstrip('!') + '.' + command.split()[1]
		except IndexError:
			plugin_command_name = ''
		# If !plug with no parameters, we turn to plugin.index
		if len(command.split()) == 1:
			plugin_command_name = command.split()[0].lstrip('!') + '.' + 'index'
		
		#make the decision!!
		if plugin_command_name.lower() in finalWhite:
			return True
		elif plugin_name.lower() in finalWhite:
			return True
		else:
			return False
		# In the event of nothing catching, we return false
		return False
	
	def register(self, user, password, group):
		'''This will register the user.'''
		import hashlib
		self.password = hashlib.sha224(password).hexdigest()
		self.nick = user.split('!')[0]
		self.hostmasks = [user.split('!')[1]]
		self.group = group
		self.registered = True
	
	def returnWhitelist(self, bot):
		# If owner group we return the whole deal
		if self.group == 'owner':
			return bot.plugins.database.keys()
		# Try to import default group from the user plugin.Might need to think of alternative if this fails.
		from plugins.user.plugin import default_group
		group_black = []
		group_white = []
		user_black = []
		user_white = []
		
		# Making sets and colleting permissions
		defaultPermissions = bot.groups.database[default_group].permissions['whitelist']
		final_black = set([])
		final_white = set([])
		final_white = set(defaultPermissions)
		
		if self.group:
			group_white = set(bot.groups.database[self.group].permissions['whitelist'])
			group_black= set(bot.groups.database[self.group].permissions['blacklist'])
		
		user_white = set(self.permissions['whitelist'])
		user_black = set(self.permissions['blacklist'])
		
		# Here we check if there are group or user permissions and overlay them
		#group_black, group_white = seterizer(group_permissions)
		# Because the default group is only a whitelist, anything in that group blacklist on the whitelist will be removed
		for g_black in group_black:
			if g_black in final_white:
				final_white = final_white.difference([g_black])
		final_black.update(group_black)
		final_white.update(group_white)
		
		#user_black, user_white = seterizer(user_permissions)
		# Now we need to remove any user whitelist from the finalblacklist, and then any userblacklist from the final whitelist
		for u_white in user_white:
			if u_white in final_black:
				final_black = final_black.difference([u_white])
		for u_black in user_black:
			if u_black in final_white:
				final_white = final_white.difference([u_black])
		final_black.update(user_black)
		final_white.update(user_white)
		
		return final_white
	
	def setPassword(self, oldPassword, newPassword):
		'''Checks if there is an existing password, then updates password.
		Returns boolian on success/failure'''
		if self.password == None: return False
		import hashlib
		if self.password == hashlib.sha224(oldPassword).hexdigest():
			self.password = self.password = hashlib.sha224(newPassword).hexdigest()
			return True
		return False
	
	def setPermissions(self, permissions):
		'''Modifies user permissions. Accepts permissions as a list of strings'''
		new_black,  new_white = self.seterizer(permissions)
		final_white = set(self.permissions['whitelist'])
		final_black = set(self.permissions['blacklist'])
		# Now the hard part.  We need to do the following
		# Check for opposite permissions and delete them
		for n_white in new_white:
			if n_white in final_black:
				final_black = final_black.difference([n_white])
		for n_black in new_black:
			if n_black in final_white:
				final_white = final_white.difference([n_black])
		# Apply the new permissions
		final_black.update(new_black)
		final_white.update(new_white)
		# Save the user file
		self.permissions['whitelist'] = list(final_white)
		self.permissions['blacklist'] = list(final_black)
	
	def seterizer(self, list):
		'''generates two sets
		one set contains all items in list that start with "-"
		the other set contains all other items'''
		black = set([])
		white = set([])
		if list[0] != '':
			for item in list:
				if item[0] == '-':
					black.add(item[1:])
				else:
					white.add(item.replace('+', ''))
		return black, white
