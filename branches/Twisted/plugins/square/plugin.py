# Square a number.  An example of a plugin taking an additional parameter
'''This is the help document which can be called by sending __doc__ as a message.'''

def load(bot):
	pass

def unload(bot):
	pass

def main (bot, user, target, msg):
	# Do we have an extra argument? If not complain!
	if len (msg.split()) == 2:
		bot.message(user, target, 'Please include a number.')
	# Try the number and return the square to the user
	else:
		try:
			number = float (msg.split[2])
			number = number ** 2
			bot.message(user, target, str(number))
		except:
			bot.message(user, target, 'Error: parameter incorrect.')
			#pass #does nothing
