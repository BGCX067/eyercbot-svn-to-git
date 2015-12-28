'''Set of functions for identifying perrmisions.'''

def checkHostmask(bot, User):
	'''Checks to see if a hostmask is present and returns that user name.'''
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
				if User.split('!')[1].lstrip('~') == host.lstrip('~'):
					name_key = key
	return name_key
