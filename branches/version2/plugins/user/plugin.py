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
'''User information and management plugin.  !user will privately display your information.  !user register registers a new account. !user set sets user parameters, type as is for help. !user permission nick +permissions -set sets permissions for that individual user. !user reload will reload the entire user database from file. !user identify nickname password will identify the user by their username and password.'''
import os
import yaml
# For importing users
import glob
# For password encryption and checking
import hashlib

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
		info(bot, user, target)
		return

	# Help
	if msg.split()[1].upper() == 'HELP' and len(msg.split()) == 2:
		bot.message(user, target, __doc__)
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
		if msg.split()[2].upper() == 'PASSWORD':
			if len(msg.split()) == 3 or len(msg.split()) == 4:
				bot.msg(user.split('!')[0], '!user set password oldpassword newpassword where oldpassword is your current password and newpassword is the new password you wish to use.')
				return None
			oldPassword = msg.split()[3]
			newPassword = msg.split()[4]
			nick = findHostmask(bot, user.split('!')[0])
			if nick:
				bot.users.database[nick].setPassword(oldPassword, newPassword)
			else:
				bot.msg(user.split('!')[0], "I don't know you by your host mask, or you put in the wrong password.")
			return None
			
	# Sets individual user permissions
	if msg.split()[1].upper() == 'PERMISSION' and len(msg.split()) > 3:
		setUserPermission(bot, msg)
		bot.message(user, target,  'Permissions set for user ' + msg.split()[2])
		
	# User can attempt to identify themselves by sumitting their password
	# If successful we will add their current hostmask 
	# !user identify nickname password
	if msg.split()[1].upper() == 'IDENTIFY' and len(msg.split()) == 4:
		nick = msg.split()[2]
		password = msg.split()[3]
		if bot.users[nick].checkPassword(password):
			bot.users[user_nick].hostmasks.append(user.split('!')[1])
			bot.users.save(nick)
			bot.msg(user.split('!')[0],  'I have identified you and added your hostmask to your user entry.')
			return None
		bot.msg(user.split('!')[0],  'That user does not exist or the password you provided did not match.')
		return
	
	if msg.split()[1].lower() == 'reload':
		bot.users.loadAll()
	# Makes a new group
	if msg.split()[1].lower() == 'new':
		if msg.split()[2].lower() == 'group' and len(msg.split()) >= 5:
			newGroup(bot, user, target, msg)
			return

# Registers a user
def register(bot, user, msg):
	'''Checks to see if user is already registered by nick or hostmask (under another name).
	Otherwise we will register the user.'''
	nick = user.split('!')[0]
	mask = user.split('!')[1]
	
	# Checks for existing name
	if nick in bot.users.database:
		if bot.users.database[nick].registered:
			bot.msg(user.split('!')[0], 'Someone is already registered as ' + name + '. If you feel this is in error, please contact one of my administrators. If it really is you please add your new hostmask.')
			return
	
	# Checks for existing hostmask
	if bot.users.findHostmask(bot, user):
		bot.msg(user.split('!')[0], 'Someone is already registered as ' + name + '. If you feel this is in error, please contact one of my administrators. If it really is you please add your new hostmask.')
		return
	
	# Ok game is on, let us register
	if len(msg.split()) == 2:
		bot.msg (user.split ('!')[0], 'Hello to you too!  Let us register you with my services.  Before we continue, make sure your current nick is the one you want me to know you by.  If it is not, type in /nick newnick (newnick is the nick you want) and send me the command again.')	
		bot.msg (user.split ('!')[0], 'Otherwise, if you are ready to continue, let us set your password.  Type in !user register yourpassword (again, replace yourpassword with a password you will remember).  This password is important as it will allow you to access your account when using a different computer.  Once your password is set it will be encrypted and I will have no way to retrieve it.  So WRITE IT DOWN!')
	elif len(msg.split()) == 3:
		# We register the new user
		if msg.split()[1].upper() == 'REGISTER':
			bot.users.makeEntry(nick)
			bot.users.database[nick].register(user, msg.split()[2], registered_group)
			# We now write the new user file
			bot.users.save(nick)
			bot.msg(user.split('!')[0], 'Thank you for registering.  There is additional information we can add to your file.  Please type in !user help for additional information!')

def setUserPermission(bot, msg):
	nick = msg.split()[2]
	# Splits the permission string into a list
	permissions = msg.split(' ', 3 )[3].split()
	bot.users.database[nick].serPermissions(permissions)
	bot.users.save(nick)
	
def returnWhitelist(bot, user):
	'''Returns whitelist of a user.'''
	if user in bot.users.database:
		return bot.user.database[user].returnWhitelist()
	
	# No user? We return default
	defaultPermissions = bot.groups.database[default_group]['permissions']['whitelist']
	finalWhite = set(defaultPermissions)
	return finalWhite

def info(bot, user, target):
	'''This will inform the user if they are registered, what group they are in, and commands availible (!help).'''
	# Are they registered?
	nick = user.split('!')[0]
	registeredName = '(not registered)'
	groupName = ''
	# We will build the output as we go
	# Identified as: Nick/(not registered), Registered: True/False, Group: Groupname, Permissions: (xrl,...), Other Parameters: (any, other, keys, present)
	output = ''
	
	if bot.users.findHostmask(user):
		registeredName = bot.users.findHostmask(user).nick
	output = 'Nick: ' + registeredName
	
	if registeredName != '(not registered)':
		if bot.users.database[registeredName].registered:
			output = output + ', Registered: True'
		else:
			output = output + ', Registered: False'
		if bot.users.database[registeredName].group:
			output = output + ', Group: ' + bot.users.database[registeredName].group
			if bot.users.database[registeredName].group.lower() == 'owner':
				output = output + ', Permissions: ' + str(bot.commands.keys())
				bot.msg(user.split ('!')[0], output)
				return None
		output = output + ', Permissions: ' + returnWhitelist(bot, registeredName)
	bot.msg (user.split ('!')[0], output)
