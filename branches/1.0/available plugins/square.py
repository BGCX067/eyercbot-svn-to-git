# Square a number.  An example of a plugin taking an additional parameter

def on_load(connection):
	pass

def on_unload(connection, event):
	pass

def index (connection, event, channels):
	# Do we have an extra argument? If not complain!
	if len (event.arguments()[0].split()) == 2:
		connection.privmsg(event.source().split('!')[0], 'Please include a number.')
	# Try the number and return the square to the user
	else:
		try:
			number = float (event.arguments()[0].split[2])
			number = number ** 2
			connection.privmsg(event.source().split('!')[0], str(number))
		except:
			connection.privmsg(event.source().split('!')[0], 'Error: parameter incorrect.')
			#pass #does nothing
