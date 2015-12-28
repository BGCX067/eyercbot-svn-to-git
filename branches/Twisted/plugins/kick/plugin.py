# kick
# kick plugin
# written by vbraun
# Version A
'''Help'''
def load(bot):
	pass
	
def main(bot,user, target, msg):
	#!kick nick (message)
	command = msg.split()
	if command[1] == "help":
		bot.message(user, target, "Syntax: !kick nick [reason]")
	else:
		if command[1] in bot.channels[event.target()].users():
			bot.kick(target, command[1], message(command))
		else:
			bot.msg(target, "No one with nick " + command[1] + " to kick!")
		
def message(event_args):
	try:
		return event_args[2]
	except:
		return ''

def unload(bot):
	pass
	
