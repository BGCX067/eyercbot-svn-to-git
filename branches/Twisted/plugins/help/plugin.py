# Help plugin
# Prints out basic help which lists commands
# Depends on user plugin

import yaml
import plugins.user.plugin as user


def load(bot):
	pass

def unload(bot):
	pass

def main(bot, user, target, msg):
	# We will want to modify th', '.join(self.command.keys())is to check for what plugins the user can do
	if msg.split()[0].upper().lstrip('!') == 'HELP':
		#connection.privmsg(event.target().split('!')[0], 'EyeRCbot Version ' + ''.join(str(version)) + ' Loaded plugins: ' + ', '.join(self.command.keys()) + ' (!plugin help for more)')
		bot.message(user, target, 'EyeRCbot Version ' + ''.join(str(bot.version)) + ' ' + str(displayHelp(bot, user)))
		
# Help text engine
# When user calls !help or !help plugin it will display what they can run

def displayHelp(bot, user):
	if bot.commands.has_key('user'):
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
		
		# The group permissions of that user is loaded
		# Which is then overlaid by the individual user permission
		# Step: Load default. Overlay group, if any. Overlay User, if any	
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
				# If the user is an owner we automaticly return full plugin list
				if group_key.upper() == 'OWNER':
					# Experiment, calling event from the bot
					return bot.commands.keys()
				print bot.groups[group_key]['permissions']
				print bot.groups[group_key]['permissions']['whitelist']
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
		final_white.update(user_white)
		white_plugs = ''
		for plug in final_white:
			white_plugs = white_plugs + plug.lower() + ', '		
		return  'Plugins: ' + white_plugs

def checkHostmask(bot, User):
	name_key = ''
	user = User.split('!')[0]
	if bot.users.has_key(user):
		if bot.users[user].has_key('hostmasks'):
			for host in bot.users[user]['hostmasks']:
				if User.split('!')[1].lstrip('~') == host.lstrip('~'):
					name_key = user
					return name_key

	keys = bot.users.keys()
	
	for key in keys:
		user = bot.users[key]
		if user.has_key('hostmasks'):
			for host in user['hostmasks']:
				if event.source().split('!')[1].lstrip('~') == host.lstrip('~'):
					name_key = key
	return name_key
