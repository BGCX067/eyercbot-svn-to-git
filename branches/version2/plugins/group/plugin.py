'''Group management plugin. Manages group permissions.'''

import yaml

# --------------------
# Configuration
config_file = open('plugins/group/config.yaml',  'r')
stream = config_file.read()
config_file.close()
groupConfig = yaml.load(stream)
# Path to the users data folder
#pathGroups = groupConfig['group_path']
# Set this to the group for all users
#defaultGroup = groupConfig['default_group']
# Set this to the group users become when registered
#registeredGroup = groupConfig['registered_group']
# --------------------

def load(bot):
	'''Load Function will go here'''
	pass

def unload(bot):
	'''Save function will go here'''
	pass

def main(bot, user, target, msg):	
	if len(msg.split()) == 1:
		# TODO: Change to print out the group the user belongs to and the permissions of that group.
		bot.message(user, target, __doc__)
		return None
	
	# Help
	if msg.split()[1].upper() == 'HELP' and len(msg.split()) == 2:
		bot.message(user, target, __doc__)
		return None

	# User sets information about self
	if msg.split()[1].upper() == 'SET':
		if len(msg.split()) == 2:
			bot.msg(user, target, '!group set default groupname changes default permission group. !group set registered groupname changes default new registered user permission group.  This is a non retroactive function. !group set permissions groupname -set permissions set permissions of that group using + or -.')
			return None

		# New default group
		if msg.split()[2].lower() == 'default':
			if len(msg.split()) == 3:
				bot.msg(user.split('!')[0], '!group set default groupname changes default permission group.')
				return None
			groupName = msg.split()[3]
			groupObject = bot.groups.findEntry(groupName)
			if groupObject:
				defaultGroup = groupName
				saveConfig()
				return
			else:
				bot.msg(user.split('!')[0], "I don't know of a group by that name.")
			return None
		
		# New registered group
		if msg.split()[2].lower() == 'registered':
			if len(msg.split()) == 3:
				bot.msg(user.split('!')[0], '!group set registered groupname changes default new registered user permission group.')
				return None
			groupName = msg.split()[3]
			groupObject = bot.groups.findEntry(groupName)
			if groupObject:
				registeredGroup = groupName
				saveConfig()
				return
			else:
				bot.msg(user.split('!')[0], "I don't know of a group by that name.")
			return None
		
		# Alters permissions
		if msg.split()[2].lower() == 'permissions' and len(msg.split()) > 4:
			groupName = msg.split()[3]
			groupObject = bot.groups.findEntry(groupName)
			if groupObject:
				permissions = msg.split(' ',4)[4].split()
				groupObject.setPermissions(permissions)
				bot.groups.save(groupName)
				bot.message(user.split('!')[0], target, "I set the new permissions for that group and saved the file.")
				return
			else:
				bot.msg(user.split('!')[0], "I don't know of a group by that name.")
				return
	if msg.split()[1].lower() == 'new' and len(msg.split()) > 3:
		bot.groups.makeEntry(msg.split()[2])
		bot.groups.database[msg.split()[2]].setPermissions(msg.split(' ',3 )[3])
		bot.groups.save(msg.split()[2])
		bot.message(user, target, 'I created and saved the new group.')

def saveConfig():
	# Configuration
	configFile = open('plugins/group/config.yaml',  'w')
	yaml.dump(groupConfig)
	configFile.close()
	
