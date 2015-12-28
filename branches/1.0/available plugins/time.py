# Plugin that displays current time or converts time from one timezone to another
# Todo: timezone conversion (pain!)

# Duh
import time

# Experimental library for time
# If this works we will want to use it 


def on_load(connection):
	pass

def on_unload(connection, event):
	pass

def index(connection, event, channels):	
	if len(event.arguments()[0].split()) == 1:
		connection.privmsg(event.target(), 'Current time in UTC: ' + time.strftime('%a, %d, %b %Y %H:%M:%S', time.gmtime()))
		return None
	
	if event.arguments()[0].split()[1].upper() == 'HELP':
		connection.privmsg(event.target(), 'Time plugin. !time current displays the current time in UTC. !time timezone, where timezone is the three letter timezone code, displays the time in that time zone. !time bottime shows the time in my timezone. !time convert time timezone1:timezone2 will convert the time entered from the first timezone into the second.')

	if event.arguments()[0].split()[1].upper() == 'CURRENT':
		connection.privmsg(event.target(), 'Current time in UTC: ' + time.strftime('%a, %d, %b %Y %H:%M:%S', time.gmtime()))

	if event.arguments()[0].split()[1].upper() == 'BOTTIME':
		connection.privmsg(event.target(), 'My current time is: ' + time.strftime('%a, %d, %b %Y %H:%M:%S', time.localtime()))
