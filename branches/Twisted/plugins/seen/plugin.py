# seen
# plugin for EyeRCBot
# written by vbraun
# Version B
# TODO: Finish fixing to match new bot system
'''
 Stores a dictionary sort of like this:
 {nick: [time, reason]}
 reads from this to tell when and why a nick left
 accounts for unlimited name changes
 pickels this dictionary into seen.txt
'''

# cPickle for faster pickle working
import cPickle as pickle
import time

def load_file():
	'''Load and unpickle, then return, the dictionary'''
	try:
		file = open("memory/seen.txt","r")
		dict = pickle.load(file)
		file.close()
	except:
		print "loading seen plugin data, failed"
		dict = {}
	return dict

def write_file(dict):
	'''Write changes to file'''
	file = open("memory/seen.txt","w")
	pickle.dump(dict,file)
	file.close()
	
def fix_time(seconds):
	'''Changes seconds into a readable format'''
	if int(seconds) >= 60:
		min = int(seconds/60)
		seconds = seconds - (min*60)
		if min >= 60:
			hour = int(min/60)
			min = min - (hour*60)
			if hour >= 24:
				day = int(hour/24)
				hour = hour - (day*24)
				return str(day) + " days " + str(hour) + " hours " + str(min) + " minutes " + str(int(seconds)) + " seconds"
			else:
				return str(hour) + " hours " + str(min) + " minutes " + str(int(seconds)) + " seconds"
		else:
			return str(min) + " minutes " + str(int(seconds)) + " seconds"
	else:
		return str(int(seconds)) + " seconds"

def load(bot):
	pass
	
def unload(bot):
	pass
	
def check_channel(nick, channel, target, c):
	'''Determines if a nick is in the channel or not'''
	if nick in channel[target].users():
		c.message(user, target, nick + " is already in the channel!")
		return False
	else:
		return True
		
def renamed(nick, c, e, ch):
	'''Checks for a renaming first, and forever until it finds the last one'''
	try:
		last_seen = load_file()
		while check_channel(nick, ch, target, c):
			#the on_nick command saves the time in the second spot so we can tell
			#we check for this to determine if a nick change occured
			if isinstance(last_seen[nick][0], (int, long, float, complex)):
				final_name(nick, c, e, ch)
				break
			else:
				time_diff = fix_time(time.time() - last_seen[nick][1])
				c.message(user, target, nick + " changed name to " + last_seen[nick][0] + ' ' + time_diff)
				nick = last_seen[nick][0]
	except:
		c.message(user, target, "Sorry, I don't think I know who " + nick + " is.")
	
def final_name(nick, c, e, ch):
	'''Returns what the last nick was doing and how long ago when last seen'''
	if check_channel(nick, ch, target, c):
		last_seen = load_file()
		info = last_seen[nick]
		time_diff = time.time() - info[0]
		c.message(user, target, nick + " was last seen " + fix_time(time_diff) + " ago, " + info[1])		
	
def main(bot, user, target, msg):
	'''recieves the command'''
	if len(msg.split()) == 2:
		request = msg.split()[1].lower()
		renamed(request, bot, event, bot.channels)
	else:
		said =msg.split()
		nick = ' '.join(said[1:len(said)])
		bot.message(user, target, "Sorry, " + nick + " is not a valid user name.")
	
def on_part(bot, event):
	last_seen = load_file()
	last_seen[event.source().split('!')[0]] = [time.time(),'parting ' + event.target()]
	write_file(last_seen)

def on_quit(bot, event):
	last_seen = load_file()
	last_seen[event.source().split('!')[0].lower()] = [time.time(),'quiting']
	write_file(last_seen)

def on_kick(bot, event):
	last_seen = load_file()
	last_seen[event.arguments()[0].lower()] = [time.time(),'being kicked from ' + event.target() + " (" + event.arguments()[1] + ")"]
	write_file(last_seen)
	
def on_nick(bot, event):
	last_seen = load_file()
	last_seen[event.source().split('!')[0].lower()] = [event.target().lower(), time.time()]
	write_file(last_seen)
	
