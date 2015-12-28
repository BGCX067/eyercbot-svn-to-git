# Admin command plugins
'''Bot administration Plugin.  !admin die will kill me. !admin load plugin name will load a plugin by that name'''
'''DO NOT USE WITHOUT USER PLUGIN
USE OWNER PLUGIN INSTEAD
OTHERWISE THE BOT WILL BE AT GREAT SECURITY RISK!!'''

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
		bot.die('My master killed me!')
	
	# Load
	# Loads all sorts of stuff from files to memory
	if msg.split()[1].upper() == 'LOAD':
		# Loads a plugin to memory (optional paramater to save it to bot config file)
		if msg.split()[2].upper() == 'PLUGIN':
			plugin = msg.split()[3]
			try:
				moduleSource = 'plugins/'+plugin+'.py'
				name = moduleSource.replace ( '.py', '' ).replace ( '\\', '/' ).split ( '/' ) [ 1 ].upper()
				handle = open ( moduleSource )
				module = imp.load_module ( name, handle, ( moduleSource ), ( '.py', 'r', imp.PY_SOURCE ) )
				bot.commands[ name ] = module
				bot.commands[name].load(bot.connection)
				bot.msg(user, target, 'I loaded your plugin.')
			except:
				bot.msg(user, target, 'I failed to load the plugin you wanted.')
