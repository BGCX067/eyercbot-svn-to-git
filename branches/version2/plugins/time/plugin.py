# Plugin that displays current time or converts time from one timezone to another
# TODO: timezone conversion (pain!)
'''Time plugin. !time current displays the current time in UTC. !time bottime shows the time in my timezone.'''

# Duh
import time

# Experimental library for time
# If this works we will want to use it 

def load(bot):
	pass

def unload(bot):
	pass

def main(bot, user, target, msg):	
	if len(msg.split()) == 1:
		bot.message(user, target, 'Current time in UTC: ' + time.strftime('%a, %d, %b %Y %H:%M:%S', time.gmtime()))
		return
	
	if msg.split()[1].upper() == 'HELP':
		bot.message(user, target, __doc__)

	if msg.split()[1].upper() == 'CURRENT':
		bot.message(user, target, 'Current time in UTC: ' + time.strftime('%a, %d, %b %Y %H:%M:%S', time.gmtime()))

	if msg.split()[1].upper() == 'BOTTIME':
		bot.message(user, target, 'My current time is: ' + time.strftime('%a, %d, %b %Y %H:%M:%S', time.localtime()))
	
	# Send ctcp request to pull self or another user's time
	#if msg.split()[1].lower() == 'mine':
	#	response = bot.ctcpMakeQuery(user.split('!')[0], ('TIME', 'Time'))
	#	bot.message(user, target, response)
