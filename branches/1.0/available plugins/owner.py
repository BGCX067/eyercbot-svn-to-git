# Owner command plugin
# While it is not required, it is needed for vital admin functions
# A custom version of the User plugin
# Will do its own permission checking in event no user module is loaded

# For scanning user files
import glob
import yaml

# Path to the users data folder
path_users = 'users/'		

owner_list = {}	

def on_load(connection):
	load_owners()

def on_unload(connection, event):
	pass

def index(connection, event, channels):	
	'''This will tell the user who they are, their host masks, their user group, what commands and modules they can or can not do.'''

	# We check right away if the user is an owner.  If not we abort.
	if checkPermission(connection, event) == False:
		connection.privmsg(event.target(), 'You are not authorized for this action.')

	# Informs the user who they are
	if len(event.arguments()[0].split()) == 1:
		connection.privmsg (event.source().split ('!')[0], 'This will eventually pm bot information and health to the user.')
		return None

	# Help
	if event.arguments()[0].split()[1].upper() == 'HELP' and len(event.arguments()[0].split()) == 2:
		connection.privmsg(event.target(), 'Bot Owner Management Plugin.  !owner die will kill me.  !owner reload  will reload all variables from disk. !owner save saves all variables to disk.')
		return None

	# Kills the bot
	if event.arguments()[0].split()[1].upper() == 'DIE':
		import EyeRCbot
		EyeRCbot.bot.die('My master killed me!')

# This will be called on to see if the user is allowed to execute command
# Returns True or False
def checkPermission(connection, event):
	# Owner permission checking engine
	user_key = checkHostmask(connection, event)
	if user_key == '':
		return False
	if owner_list.has_key(user_key) == True:
		return True

# We check the password to see if command is allowed
# We do this two ways, first we see if a user file is present and if the password matches
# If this doesn't work we scan the user files for the hostmask and use that user file to check the password
# Returns true(match) or false(no match), user key
def checkPassword(connection, event, password):
	# We hash the password
	password = hashlib.sha224(password).hexdigest()
	user = event.source().split('!')[0]
	if user_list.has_key(user) == True:
		save_password = user_list[user]['password']
		if save_password == password:
			return (True, user)
		else:
			return (False, '')
	# No existing user name, so now we try to find another match by hostmask
	user = checkHostmask(connection, event)
	save_password = user_list[user]['password']
	if save_password == password:
		return (True, user)
	return (False, '')

# We scan for the user key of the hostmask
# Returns key name
def checkHostmask(connection, event):
	keys = owner_list.keys()
	name_key = ''
	for key in keys:
		user = owner_list[key]
		for host in user['hostmasks']:
			if event.source().split('!')[1] == host:
				name_key = key
	return name_key

def load_owners():
	owner_list.clear()
	# We scan the user folder and load owners into a dictionary
	for userSource in glob.glob ( path_users + '*.yaml' ):
		name = userSource.replace ( '.yaml', '' ).replace ( '\\', '/' ).split ( '/' ) [ 1 ]
		user_file = open(userSource)
		stream = user_file.read()
		user_file.close()
		user = yaml.load(stream)
		if user.has_key('group') == True:
			if user['group'].upper() == 'OWNER':
				owner_list['name'] = user
