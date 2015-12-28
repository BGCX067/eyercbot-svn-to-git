'''Class for groups.'''

class Group(object):
	'''Group class. Takes the bot parameter in case we need to access the bot.'''
	def __init__(self, bot, name=None):
		self.name = name
		self.permissions = {'whitelist': [], 'blacklist': []}
	
	def setPermissions(self, permissions):
		'''Modifies group permissions. Accepts permissions as a list of strings
		'''
		print permissions
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
