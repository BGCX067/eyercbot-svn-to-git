# Help plugin
# Prints out basic help which lists commands
# Depends on user plugin

import yaml

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
	userObject = bot.users.getUser(user)
	whitePlugs = userObject.returnWhitelist(bot)
	plugList = ''
	for plug in whitePlugs:
		plugList = plugList + ' ' + plug + ','
	return  'Plugins: ' + plugList.rstrip(',')


