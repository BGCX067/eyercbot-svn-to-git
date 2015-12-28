# Owner command plugin
# While it is not required, it is needed for vital admin functions
# A custom version of the User plugin
# Will do its own permission checking in event no user module is loaded
'''Bot Owner Management Plugin.  !owner die will kill me.  !owner reload  will reload all variables from disk. !owner save saves all variables to disk.'''
# For scanning user files
import glob
import EyeRClib.yaml as yaml

# Path to the users data folder
path_users = 'users/'		

owner_list = {}	

def load(bot):
	load_owners()

def unload(bot):
	pass

def main(bot, user, target, msg):	
	'''This will tell the user who they are, their host masks, their user group, what commands and modules they can or can not do.'''

	# We check right away if the user is an owner.  If not we abort.
	if checkPermission(bot, user, target, msg) == False:
		bot.message(user, target, 'You are not authorized for this action.')
		return None

	# Informs the user who they are
	if len(msg.split()) == 1:
		bot.message(user, target, 'This will eventually pm bot information and health to the user.')
		return None

	# Help
	if msg.split()[1].upper() == 'HELP' and len(msg.split()) == 2:
		bot.message(user, target, __doc__)
		return None

	# Kills the bot
	if msg.split()[1].upper() == 'DIE':
		bot.die('My master killed me!')

# This will be called on to see if the user is allowed to execute command
# Returns True or False
def checkPermission(bot, user, target, msg):
	# Owner permission checking engine
	user_key = checkHostmask(user)
	if owner_list.has_key(user_key) == True:
		return True
	return False

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
def checkHostmask(user):
	keys = owner_list.keys()
	name_key = ''
	for key in keys:
		user = owner_list[key]
		for host in user['hostmasks']:
			if user.split('!')[1] == host:
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
			try:
				if user['group'].upper() == 'OWNER':
					owner_list['name'] = user
			except:
					pass
