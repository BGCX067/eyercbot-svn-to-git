# This script will manage the user database
# Objectives:  Users will be recognized by their host mask(s)
# Users will be placed in groups (general is the default)
# Groups will have -command masks
# Users will have -command and +command masks, these will override group settings
# -Module.Command override +Module (and vice verse)
# +- ALL, which is overrides by -Command
# Take a look at supybots code on how they implement this.
# Each user will have an individual file in their users folder

# Actual user info storred as a dict into user_list as follows: 
#{name: {"property1": "value1", "property": ["with", "more", "than", "one value"] ..etc

import os
import yaml
# For importing users
import glob
# For password encryption and checking
import hashlib
# Access user and group dict
import EyeRCbot

# ----------
# Configuration
# Path to the users data folder
path_users = 'users/'
path_groups = 'groups/'
# Set this to the group for all users
default_group = 'default'
# Set this to the group users become when registered
registered_group = 'default'
# ----------

		

def on_load(connection):
	pass

def on_unload(connection, event):
	pass

def index(connection, event, channels):	
	'''This will tell the user who they are, their host masks, their user group, what commands and modules they can or can not do.'''

	# Informs the user who they are
	if len(event.arguments()[0].split()) == 1:
		connection.privmsg (event.source().split ('!')[0], 'You are you.  There are currently no commands you can run or are banned from.  In fact there is nothing here.  !user help will provide information for this.')
		return None

	# Help
	if event.arguments()[0].split()[1].upper() == 'HELP' and len(event.arguments()[0].split()) == 2:
		connection.privmsg(event.target(), 'User information and management plugin.  !user will privately display your information.  !user register registers a new account. !user set sets user parameters, type as is for help.')
		return None


	# Allows the user to register
	if event.arguments()[0].split()[1].upper() == 'REGISTER':
		register(connection, event)
		return None
		
	# User sets information about self
	if event.arguments()[0].split()[1].upper() == 'SET':
		
		if len(event.arguments()[0].split()) == 2:
			connection.privmsg(event.target(), '!user set password oldpassword newpassword changes user password.')
			return None

		# User sets a new password
		if event.arguments()[0].split()[2].upper() == 'PASSWORD':
			if len(event.arguments()[0].split()) == 3 or len(event.arguments()[0].split()) == 4:
				connection.privmsg(event.source().split('!')[0], '!user set password oldpassword newpassword where oldpassword is your current password and newpassword is the new password you wish to use.')
				return None
			old_password = event.arguments()[0].split()[3]
			new_password = event.arguments()[0].split()[4]
			is_user = checkPassword(connection, event, old_password)
			if is_user[0] == True:
				EyeRCbot.bot.user_list[is_user[1]]['password'] = new_password
				user_dict = user_list[is_user[1]]
				stream = file(path_users + is_user[1] + '.yaml', 'w')
				yaml.dump(user_dict, stream)
				stream.close()
				connection.privmsg(event.source().split('!')[0], 'Your new password is saved.')
			else:
				connection.privmsg(event.source().split('!')[0], "I don't know you by your name or host mask, or you put in the wrong password.")
			return None


# This will be called on to see if the user is allowed to execute command
# Returns True or False
def checkPermission(connection, event):
	# New permission checking engine
	# The group permissions of that user is loaded
	# Which is then overlaid by the individual user permission
	# Step: Load default. Overlay group, if any. Overlay User, if any	
	default_permissions = EyeRCbot.bot.group_list[default_group]['permissions']
	group_permissions = None
	user_permissions = None
	user_key = checkHostmask(connection, event)

	#making sets..
	final_black = set([])
	final_white = set([])

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
					white.add(item)
		return black, white
	default_black, default_white = seterizer(default_permissions)

	# If the user is not registered we just use the default permissions
	if user_key != '':
		if EyeRCbot.bot.user_list[user_key].has_key('group') == True:
			group_key = EyeRCbot.bot.user_list[user_key]['group']
			group_permissions = EyeRCbot.bot.group_list[group_key]['permissions']
			# If the user is an owner we automaticly return true
			if group_key.upper() == 'OWNER':
				return True
	
		if EyeRCbot.bot.user_list[user_key].has_key('permissions') == True:
			user_permissions = EyeRCbot.bot.user_list[user_key]['permissions']

	# Here we check if there are group or user permissions and overlay them
	if group_permissions != None:
		group_black, group_white = seterizer(group_permissions)
		final_black.update(group_black)
		final_white.update(group_white)

	if user_permissions != None:
		user_black, user_white = seterizer(user_permissions)
		final_black.update(user_black)
		final_white.update(user_white)
		
	#Adds the elements that are unique to the second set to the final set
	final_black.update(default_black)
	final_white.update(default_white)

	#get a set of items that are in both sets
	final_conflicts = final_white & final_black
	#take out the conflicted items and make the final set
	final = (final_white - final_conflicts) - (final_black - final_conflicts)
	#resolve conflicts in this order: user, group, default
	try:
		for item in final_conflicts:
			if item in user_white:
				final.add(item)
			elif item not in user_black:
				if item in group_white:
					final.add(item)
				elif item not in group_black:
					#I think it should never get this far, but just in case
					if item in default_white:
						final.add(item)
					elif item not in default_black:
						#It definetly should never get here
						print "PROBLEM IN DETERMINING USABLE PLUGINS!!!"
						print "A conflict has occured but it isn't in user or group or default definitions"
	except UnboundLocalError:
		pass

	# Can the user use the plugin at all?
	plugin_name = event.arguments()[0].split()[0].lstrip('!')
	#check for a multi word command
	try:
		plugin_command_name = event.arguments()[0].split()[0].lstrip('!') + '.' + event.arguments()[0].split()[1]
	except IndexError:
		plugin_command_name = ''
	
	#make the decision!!
	if plugin_name in final:
		return True
	elif plugin_command_name in final:
		return True
	else:
		return False

	# If the command length is one word, and there is no explicit permission we say they can't use it
	if len(event.arguments()[0].split()) == 1:
		return False

	return False

# We check the password to see if command is allowed
# We do this two ways, first we see if a user file is present and if the password matches
# If this doesn't work we scan the user files for the hostmask and use that user file to check the password
# Returns true(match) or false(no match), user key
def checkPassword(connection, event, password):
	# We hash the password
	password = hashlib.sha224(password).hexdigest()
	user = event.source().split('!')[0]
	if EyeRCbot.bot.user_list.has_key(user) == True:
		save_password = EyeRCbot.bot.user_list[user]['password']
		if save_password == password:
			return (True, user)
		else:
			return (False, '')
	# No existing user name, so now we try to find another match by hostmask
	user = checkHostmask(connection, event)
	save_password = EyeRCbot.bot.user_list[user]['password']
	if save_password == password:
		return (True, user)
	return (False, '')

# We scan for the user key of the hostmask
# Returns key name
def checkHostmask(connection, event):
	keys = EyeRCbot.bot.user_list.keys()
	name_key = ''
	for key in keys:
		user = EyeRCbot.bot.user_list[key]
		for host in user['hostmasks']:
			if event.source().split('!')[1] == host:
				name_key = key
	return name_key

# Registers a user
def register(connection, event):
	# We need to do a hostmask check to see if they are registered under another name, then ask them if they want to change their registered name
	# This sees if the username making the request is in the database
	# If so we abort telling the user someone has registered in that name
	user_name = event.source().split('!')[0]
	for name in EyeRCbot.bot.user_list:
		if name == user_name and EyeRCbot.bot.user_list[name].has_key('is_registered'):
			connection.privmsg(event.source().split('!')[0], 'Someone is already registered as ' + name + '. If you feel this is in error, please contact one of my administrators. If it really is you please add your new hostmask.')
			return None

	if len(event.arguments()[0].split()) == 2:
		connection.privmsg (event.source().split ('!')[0], 'Hello to you too!  Let us register you with my services.  Before we continue, make sure your current nick is the one you want me to know you by.  If it is not, type in /nick newnick (newnick is the nick you want) and send me the command again.')	
		connection.privmsg (event.source().split ('!')[0], 'Otherwise, if you are ready to continue, let us set your password.  Type in !user register yourpassword (again, replace yournewpassword with a password you will remember).  This password is important as it will allow you to access your account when using a different computer.  Once your password is set it will be encrypted and I will have no way to retrieve it.  So WRITE IT DOWN!')
	elif len(event.arguments()[0].split()) == 3:
		# We register the new user
		if event.arguments()[0].split()[1].upper() == 'REGISTER':
			# We encrypt the password
			password = hashlib.sha224(event.arguments()[0].split()[2]).hexdigest()
			# We now generate the user in the userlist and insert the password and hostmask of the user
			host_mask = event.source().split('!')[1]
			new_user = {}
			new_user['name'] = user_name
			new_user['hostmasks'] = [host_mask]
			new_user['password'] = password
			new_user['group'] = registered_group
			new_user['permissions'] = ['']
			new_user['is_registered'] = True

			if EyeRCbot.bot.user_list.has_key(user_name) == True:
				EyeRCbot.bot.user_list[user_name].update(new_user)
			else:
				EyeRCbot.bot.user_list[user_name] = new_user
			# We now write the new user file
			stream = file(path_users + user_name + '.yaml', 'w')
			yaml.dump(new_user, stream)
			stream.close()
			connection.privmsg(event.source().split('!')[0], 'Thank you for registering.  There is additional information we can add to your file.  Please type in !user help for additional information!')

def setUserPermission(connection, event):
	pass

def setGroupPermission(connection, event):
	pass
