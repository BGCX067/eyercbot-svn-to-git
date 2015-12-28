# This script will manage the user database
# Objectives:  Users will be recognized by their host mask(s)
# Users will be placed in groups (general is the default)
# Groups will have +command and -command masks (default only needs +command)
# Users will have -command and +command masks, these will override group settings
# -Module.Command override +Module (and vice verse)
# +- ALL, which is overrides by -Command
# Take a look at supybots code on how they implement this.
# Each user will have an individual file in their users folder

# Actual user info storred as a dict into user_list as follows: 
#{name: {"property1": "value1", "property": ["with", "more", "than", "one value"] ..etc
'''User information and management plugin.  !user will privately display your information.  !user register registers a new account. !user set sets user parameters, type as is for help. !user permission nick +permissions -set sets permissions for that individual user'''
import os
import yaml
# For importing users
import glob
# For password encryption and checking
import hashlib
import EyeRClib.diskio as diskio

# --------------------
# Configuration
config_file = open('plugins/user/config.yaml',  'r')
stream = config_file.read()
config_file.close()
users_config = yaml.load(stream)
# Path to the users data folder
path_users = users_config['user_path']
path_groups = users_config['group_path']
# Set this to the group for all users
default_group = users_config['default_group']
# Set this to the group users become when registered
registered_group = users_config['registered_group']
# --------------------


def load(bot):
	pass

def unload(bot):
	pass

def main(bot, user, target, msg):	
	'''This will tell the user who they are, their host masks, their user group, what commands and modules they can or can not do.'''

	# Informs the user who they are
	if len(msg.split()) == 1:
		# We will tell the user if they are registered, if so what gorup they are in, what commands they can do (standard !help), and basicly dump their dict on them
		# Are they registered?
		user_name = user.split('!')[0]
		registered_name = '(not registered)'
		group_name = ''
		# We will build the output as we go
		# Identified as: Nick/(not registered), Registered: True/False, Group: Groupname, Permissions: (xrl,...), Other Parameters: (any, other, keys, present)
		output = ''
		# Hack until we move to a new variable name
		
		for name in bot.users:
			if name == user_name and bot.users[name].has_key('is_registered'):
				registered_name = name
		# We scan fror their hostmask in the event they are another name
		if registered_name == '(not registered)':
			user_name = checkHostmask(bot, user)
			if user_name != '':
				registered_name = user_name
		
		output = 'Nick: ' + registered_name
		
		if registered_name != '(not registered)':
			if bot.users[registered_name].has_key('is_registered') == False:
				output = output + ', Registered: False'
			else:
				output = output + ', Registered: True'
			if bot.users[registered_name].has_key('group') :
				output = output + ', Group: ' + bot.users[registered_name]['group']
				if bot.users[registered_name]['group'].upper() == 'OWNER':
					output = output + ', Permissions: ' + str(bot.commands.keys())
					bot.msg (user.split ('!')[0], output)
					return None
			output = output + ', Permissions: ' + returnWhitelist(bot, registered_name)
		bot.msg (user.split ('!')[0], output)
		return None

	# Help
	if msg.split()[1].upper() == 'HELP' and len(msg.split()) == 2:
		bot.msg(user, target, __doc__)
		return None

	# Allows the user to register
	if msg.split()[1].upper() == 'REGISTER':
		register(bot, user, msg)
		return None
		
	# User sets information about self
	if msg.split()[1].upper() == 'SET':
		if len(msg.split()) == 2:
			bot.msg(user, target, '!user set password oldpassword newpassword changes user password.')
			return None

		# User sets a new password
		if emsg.split()[2].upper() == 'PASSWORD':
			if len(msg.split()) == 3 or len(msg.split()) == 4:
				bot.msg(user.split('!')[0], '!user set password oldpassword newpassword where oldpassword is your current password and newpassword is the new password you wish to use.')
				return None
			old_password = msg.split()[3]
			new_password = msg.split()[4]
			is_user = checkPassword(old_password)
			if is_user[0] == True:
				bot.users[is_user[1]]['password'] = new_password
				user_dict = bot.users[is_user[1]]
				stream = file(path_users + is_user[1] + '.yaml', 'w')
				yaml.dump(user_dict, stream)
				stream.close()
				bot.msg(user.split('!')[0], 'Your new password is saved.')
			else:
				bot.msg(user.split('!')[0], "I don't know you by your name or host mask, or you put in the wrong password.")
			return None
			
	# Sets individual user permissions
	if msg.split()[1].upper() == 'PERMISSION' and len(msg.split()) > 3:
		setUserPermission(bot, msg)
		bot.message(user, target,  'Permissions set for user ' + msg.split()[2])
		
	# User can attempt to identify themselves by sumitting their password
	# If successful we will add their current hostmask 
	# !user identify nickname password
	if msg.split()[1].upper() == 'IDENTIFY' and len(msg.split()) == 4:
		user_nick = msg.split()[2]
		password = msg.split()[3]
		if checkPassword2(bot, user_nick, password) == True:
			bot.users[user_nick]['hostmasks'].append(user.split('!')[1])
			diskio.save_user(bot, user_nick)
			bot.msg(user.split('!')[0],  'I have identified you and added your hostmask to your user entry.')
			return None
		bot.msg(user.split('!')[0],  'That user does not exist or the password you provided did not match.')

# This will be called on to see if the user is allowed to execute command
# Returns True or False
def checkPermission(bot, user, msg):
	# The group permissions of that user is loaded
	# Which is then overlaid by the individual user permission
	# Step: Load default. Overlay group, if any. Overlay User, if any	
	
	# We are now allowing a new permission plug.index, which allows !plugin with no command parameters
	default_permissions = bot.groups[default_group]['permissions']['whitelist']
	group_black = []
	group_white = []
	user_black = []
	user_white = []
	
	user_key = checkHostmask(bot, user)
	if user_key == '':
		if bot.users.has_key(user.split('!')[0]):
			if bot.users[user.split('!')[0]].has_key('permissions'):
				user_key = user.split('!')[0]

	#making sets..
	final_black = set([])
	final_white = set([])
	final_white = set(default_permissions)

	# If the user is not registered we just use the default permissions
	if user_key != '':
		if bot.users[user_key].has_key('group') == True:
			group_key = bot.users[user_key]['group']
			# If the user is an owner we automaticly return true
			if group_key.upper() == 'OWNER':
				return True
			group_white = set(bot.groups[group_key]['permissions']['whitelist'])
			group_black= set(bot.groups[group_key]['permissions']['blacklist'])
		print user_key
		print bot.users[user_key]['permissions']['whitelist']
		if bot.users[user_key].has_key('permissions') == True:
			user_white = set(bot.users[user_key]['permissions']['whitelist'])
			user_black = set(bot.users[user_key]['permissions']['blacklist'])
	
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
		
	# Can the user use the plugin at all?
	plugin_name = msg.split()[0].lstrip('!')
	#check for a multi word command
	try:
		plugin_command_name = msg.split()[0].lstrip('!') + '.' + msg.split()[1]
	except IndexError:
		plugin_command_name = ''
	# If !plug with no parameters, we turn to plugin.index
	if len(msg.split()) == 1:
		plugin_command_name = msg.split()[0].lstrip('!') + '.' + 'index'
	
	#make the decision!!
	if plugin_command_name.lower() in final_white:
		return True
	elif plugin_name.lower() in final_white:
		return True
	else:
		return False
	# In the event of nothing catching, we return false
	return False

# We check the password to see if command is allowed
# We do this two ways, first we see if a user file is present and if the password matches
# If this doesn't work we scan the user files for the hostmask and use that user file to check the password
# Returns true(match) or false(no match), user key
def checkPassword(password):
	# We hash the password
	password = hashlib.sha224(password).hexdigest()
	user = event.source().split('!')[0]
	if bot.users.has_key(user) == True:
		save_password = bot.user_list[user]['password']
		if save_password == password:
			return (True, user)
		else:
			return (False, '')
	# No existing user name, so now we try to find another match by hostmask
	user = checkHostmask(bot, connection, event)
	save_password = bot.users[user]['password']
	if save_password == password:
		return (True, user)
	return (False, '')
	
# New password checker which only checks the password of that nick
def checkPassword2(bot, user,  password):
	# We hash the password
	password = hashlib.sha224(password).hexdigest()
	if bot.users.has_key(user) == True:
		if bot.users[user].has_key('password'):
			save_password = bot.user_list[user]['password']
			if save_password == password:
				return True
	return False

# We scan for the user key of the hostmask
# Returns key name
# Let us try something new to make things a little more efficient
# First, we see if the bot has the user name
# Second, we see if that user name has the hostmask and return key if true
# Otherwise, continue as usual
def checkHostmask(bot, user):
	print user
	name_key = ''
	u = user.split('!')[0]
	if bot.users.has_key(user):
		if bot.users[u].has_key('hostmasks'):
			for host in bot.users[u]['hostmasks']:
				if user.split('!')[1].lstrip('~') == host.lstrip('~'):
					name_key = u
					return name_key

	for key in bot.users.keys():
		if 'hostmasks' in bot.users[key]:
			for host in bot.users[key]['hostmasks']:
				if user.split('!')[1].lstrip('~') == host.lstrip('~'):
					name_key = key
	return name_key

# Registers a user
def register(bot, user, msg):
	# We need to do a hostmask check to see if they are registered under another name, then ask them if they want to change their registered name
	# This sees if the username making the request is in the database
	# If so we abort telling the user someone has registered in that name
	user_name = user.split('!')[0]
	for name in bot.users:
		if name == user_name and bot.users[name].has_key('is_registered'):
			bot.msg(user.split('!')[0], 'Someone is already registered as ' + name + '. If you feel this is in error, please contact one of my administrators. If it really is you please add your new hostmask.')
			return None

	if len(msg.split()) == 2:
		bot.msg (user.split ('!')[0], 'Hello to you too!  Let us register you with my services.  Before we continue, make sure your current nick is the one you want me to know you by.  If it is not, type in /nick newnick (newnick is the nick you want) and send me the command again.')	
		bot.msg (user.split ('!')[0], 'Otherwise, if you are ready to continue, let us set your password.  Type in !user register yourpassword (again, replace yourpassword with a password you will remember).  This password is important as it will allow you to access your account when using a different computer.  Once your password is set it will be encrypted and I will have no way to retrieve it.  So WRITE IT DOWN!')
	elif len(msg.split()) == 3:
		# We register the new user
		if msg.split()[1].upper() == 'REGISTER':
			# We encrypt the password
			password = hashlib.sha224(msg.split()[2]).hexdigest()
			# We now generate the user in the userlist and insert the password and hostmask of the user
			host_mask = user.split('!')[1]
			new_user = {}
			new_user['name'] = user_name
			new_user['hostmasks'] = [host_mask]
			new_user['password'] = password
			new_user['group'] = registered_group
			new_user['permissions'] = {'whitelist': [],  'blacklist': []}
			new_user['is_registered'] = True

			if bot.users.has_key(user_name) == True:
				bot.users[user_name].update(new_user)
			else:
				bot.users[user_name] = new_user
			# We now write the new user file
			stream = file(path_users + user_name + '.yaml', 'w')
			yaml.dump(new_user, stream)
			stream.close()
			bot.msg(user.split('!')[0], 'Thank you for registering.  There is additional information we can add to your file.  Please type in !user help for additional information!')

def setUserPermission(bot, msg):
	user_nick = msg.split()[2]
	# Splits the permission string into a list
	permission_list = msg.split(' ', 3 )[3].split()
	new_black,  new_white = seterizer(permission_list)
	# We see if there is existing permissions for that user, if not we generate it
	if bot.users.has_key(user_nick) == False:
		bot.users[user_nick] = {}
	if bot.users[user_nick].has_key('permissions') == False:
		bot.users[user_nick]['permissions'] = {'whitelist':[], 'blacklist':[]}
	final_white = set(bot.users[user_nick]['permissions']['whitelist'])
	final_black = set(bot.users[user_nick]['permissions']['blacklist'])
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
	bot.users[user_nick]['permissions']['whitelist'] = list(final_white)
	bot.users[user_nick]['permissions']['blacklist'] = list(final_black)
	# We now write the new user file
	stream = file(path_users + user_nick + '.yaml', 'w')
	yaml.dump(bot.users[user_nick], stream)
	stream.close()

def setGroupPermission(bot, event):
	group_nick = event.arguments()[0].split()[2]
	# Splits the permission string into a list
	permission_list = event.arguments()[0].split(' ', 3 )[3].split()
	new_black,  new_white = seterizer(permission_list)
	# We see if there is existing permissions for that group, if not we generate it
	if bot.groups.has_key(group_nick) == False:
		bot.groups[group_nick] = {'name': group_nick}
	if bot.groups[group_nick].has_key('permissions') == False:
		bot.groups[group_nick]['permissions'] = {'whitelist':[], 'blacklist':[]}
	final_white = set(bot.groups[group_nick]['permissions']['whitelist'])
	final_black = set(bot.groups[group_nick]['permissions']['blacklist'])
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
	# Save the group file
	bot.groups[group_nick]['permissions']['whitelist'] = list(final_white)
	bot.groups[group_nick]['permissions']['blacklist'] = list(final_black)
	# We now write the new group file
	stream = file(path_groups + group_nick + '.yaml', 'w')
	yaml.dump(bot.groups[group_nick], stream)
	stream.close()
	
def seterizer(list):
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

def returnWhitelist(bot, user_key):
	# The group permissions of that user is loaded
	# Which is then overlaid by the individual user permission
	# Step: Load default. Overlay group, if any. Overlay User, if any	
	
	# We are now allowing a new permission plug.index, which allows !plugin with no command parameters
	default_permissions = bot.groups[default_group]['permissions']['whitelist']
	group_black = []
	group_white = []
	user_black = []
	user_white = []

	#making sets..
	final_black = set([])
	final_white = set([])
	final_white = set(default_permissions)

	# If the user is not registered we just use the default permissions
	if user_key != '':
		if bot.users[user_key].has_key('group') == True:
			group_key = bot.users[user_key]['group']
			# If the user is an owner we automaticly return true
			if group_key.upper() == 'OWNER':
				return True
			group_white = set(bot.groups[group_key]['permissions']['whitelist'])
			group_black= set(bot.groups[group_key]['permissions']['blacklist'])
	
		if bot.users[user_key].has_key('permissions') == True:
			user_white = set(bot.users[user_key]['permissions']['whitelist'])
			user_black = set(bot.users[user_key]['permissions']['blacklist'])
	
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
