# Channel managment plugin
# Managaes channels - auto op, auto ban, mode changes
# !channel moderate list of nicks not to auto voice
# We want to autoop people with the user['mode'] parameter
# Requires User plugin installed to check for hostmask
# Current commands
# !kick user
# 

import yaml
import plugins.user.plugin as user

path_users = 'users/'

def load(bot):
	pass

def unload(bot):
	pass
	
def main(bot, event):
	command = event.arguments()[0].split()
	if len(command) == 1:
		bot.message(event,  'Channel management plugin. !channel kick user, !channel autoop user.')
		return None
	
	if event.arguments()[0].split()[1].upper() == 'KICK':
		if command[2] in channel[event.target()].users():
			bot.connection.kick(event.target(), command[1], message(command))
		else:
			bot.connection.privmsg(event.target(), "No one with nick " + command[1] + " to kick!")

	if event.arguments()[0].split()[1].upper() == 'AUTOOP' and len(command) == 3:
		add_mode('+o', command[2])
		bot.connection.privmsg(event.target(), 'Added +o' + ' to ' + command[2])

def on_join(bot, event):
	# If a user joins, we check for modes then apply
	nick = event.source().split('!')[0]
	chan = event.target()
	if bot.users.has_key(nick) == True:
		if bot.users[nick].has_key('modes') == True:
			for mode in bot.users[nick]['modes']:
				bot.connection.mode(chan, mode + ' ' + nick)
	else:
		nick = user.checkHostmask(bot, event)
		if bot.users.has_key(nick) == True:
			if bot.users[nick].has_key('modes') == True:
				for mode in bot.users[nick]['modes']:
					bot.connection.mode(chan, mode + ' ' + nick)
		
def message(event_args):
	try:
		return event_args[2]
	except:
		return ''

def add_mode(mode, nick):
	if bot.users.has_key(nick) == False:
		bot.users[nick] = {'modes':[mode]}
	elif bot.users[nick].has_key('modes') == False:
		bot.users[nick]['modes'] = [mode]
	else:
		# Does user have mode (or inverse) already?
		for modes in bot.users[nick]['modes']:
			if modes.strip('+-') == mode.strip('+-'):
				bot.users[nick]['modes'][modes] = mode
				break
		else: 
			bot.users[nick]['modes'][modes] = mode
	stream = file(path_users + nick + '.yaml', 'w')
	yaml.dump(bot.users[nick], stream)
	stream.close()

