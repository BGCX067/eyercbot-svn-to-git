# Disk I/O Library
# This module provides the common operations needed for writing a file to disk.
# This should clean up code uberly!

# --------------------
# Configuration
# Path to users
path_users = 'users/'
# Path to groups
path_groups = 'groups/'
# --------------------

import yaml
import glob

# Loads all users from file
# This will clear the users in the bot memory
# Make sure to save the user file first for normal operation!
def load_users(bot):
	bot.users.clear()
	# We scan the user folder and load them into a dictionary
	# Issues with directories (ie .svn).  Look into os.walk?
	for userSource in glob.glob ( path_users + '*.yaml' ):
		name = userSource.replace ( '.yaml', '' ).replace ( '\\', '/' ).split ( '/' ) [ 1 ]
		user_file = open(userSource)
		stream = user_file.read()
		user_file.close()
		bot.users[name] = yaml.load(stream)

# Load all groups from file
# This will clear existing groups from memory
# So safe first!
def load_groups(bot):
	bot.groups.clear()
	# We scan the user folder and load them into a dictionary
	# Issues with directories (ie .svn).  Look into os.walk?
	for groupSource in glob.glob ( path_groups + '*.yaml' ):
		name = groupSource.replace ( '.yaml', '' ).replace ( '\\', '/' ).split ( '/' ) [ 1 ]
		group_file = open(groupSource)
		stream = group_file.read()
		group_file.close()
		bot.groups[name] = yaml.load(stream)

# Save all or a user to file
def save_user(bot, user='ALL'):
	if user == 'ALL':
		print bot.user_list
		for user_name in bot.users:
			stream = file(path_users + user_name + '.yaml', 'w')
			yaml.dump(bot.users[user_name], stream)
			stream.close()
	else:
		stream = file(path_users + user + '.yaml', 'w')
		yaml.dump(bot.users[user], stream)
		stream.close()
