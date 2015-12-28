# Logins to nickserv on join
# Nickserv pass
password = 'password'

def load(bot):
	pass

def unload(bot):
	pass

def main(bot, user, target, msg):
	pass

def signedOn (bot):
	bot.msg('NICKSERV', 'IDENTIFY ' + password)
