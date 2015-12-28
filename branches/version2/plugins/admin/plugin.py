# Admin command plugins
'''Bot administration Plugin.  !admin die will kill me. !admin load plugin name will load a plugin by that name'''

import imp

def load(bot):
	pass

def unload(bot):
	pass

def main(bot, user, target, msg):
	# Informs the user who they are
	if len(msg.split()) == 1:
		bot.message(user, target,  'This will eventually pm bot information and health to the user.')
		return None

	# Help
	if msg.split()[1].upper() == 'HELP' and len(msg.split()) == 2:
		bot.message(user, target, __doc__ )
		return None

	# Kills the bot
	if msg.split()[1].upper() == 'DIE':
		bot.quit('My master killed me!')
	
	# Load
	# Loads all sorts of stuff from files to memory
	if msg.split()[1].upper() == 'LOAD':
		# Loads a plugin to memory (optional paramater to save it to bot config file)
		if msg.split()[2].upper() == 'PLUGIN':
			plugin = msg.split()[3]
			bot.plugins.load(plugin)
	
	# Save config file
	
	# Output to user some content of the bot
	if msg.split()[1].lower() == 'print':
		bot.message(user, target,  eval(msg.split()[2]))
		
