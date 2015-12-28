# kick
# kick plugin
# written by vbraun
# Version A

def on_load(connection):
	pass
	
def index(connection, event, channel):
	#!kick nick (message)
	command = event.arguments()[0].split()
	if command[1] == "help":
		connection.privmsg(event.target(), "Syntax: !kick nick [reason]")
	else:
		if command[1] in channel[event.target()].users():
			connection.kick(event.target(), command[1], message(command))
		else:
			connection.privmsg(event.target(), "No one with nick " + command[1] + " to kick!")
		
def message(event_args):
	try:
		return event_args[2]
	except:
		return ''

def on_unload(connection, event):
	pass
	