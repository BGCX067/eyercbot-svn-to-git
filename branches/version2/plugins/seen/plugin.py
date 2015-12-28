# seen
# plugin for EyeRCBot
# written by vbraun
# upgraded to 2.x series by croxis
# Version C
# TODO: Finish fixing to match new bot system
'''
 Stores a dictionary sort of like this:
 channelObject.nickHistory = {nick: [time, reason]}
 
  
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
	for chan in bot.channels.database:
		try:
			if bot.channels.database[chan].nickHistory:
				pass
		except:
			bot.channels.database[chan].nickHistory = {}
	
def unload(bot):
	pass
	
def main(bot, user, target, msg):
	'''recieves the command'''
	if len(msg.split()) == 2:
		request = msg.split()[1].lower()
		search(bot, request, user, target)
	else:
		said =msg.split()
		nick = ' '.join(said[1:len(said)])
		bot.message(user, target, "Sorry, " + nick + " is not a valid user name.")
	
def userLeft(bot, user, channel):
	bot.channels.database[channel].nickHistory[user.split('!')[0]] = [time.time(),'parting ' + channel]

def userQuit(bot, user, message):
	bot.channels.database[channel].nickHistory[user.split('!')[0]] = [time.time(),'quiting']

def userKicked(bot, kickee, channel, kicker, message):
	bot.channels.database[channel].nickHistory[kickee.lower()] = [time.time(),'being kicked from ' + channel + " (" + message + ")"]
	
def userRenamed(bot, oldname, newname):
	for chan in bot.channels.database:
			if oldname.split('!') in bot.channels.database[chan].nicks:
				bot.channels.database[channel].nickHistory[oldname.split('!')[0].lower()] = [newname.lower(), time.time()]
	
def search(bot, request, user, channel):
	'''
	Searches for user in channels and history.
	'''
	# TODO: Allow search for all channels or a defined one
	# Step 1: Is request in channel(s)?
	print request.lower()
	if  bot.channels.findEntry(request.lower()):
		bot.message(user, channel, request + 'is already in this channel silly.')
		return
	
	# Step 2: We see if the entry is present, and if it was renamed
	while bot.channels.findEntry(request.lower()) == None:
		try:
			if isinstance(bot.channels.database[channel].nickHistory[request][0], (int, long, float, complex)):
				print 1
				info = bot.channels.database[channel].nickHistory[request]
				print 3
				time_diff = time.time() - info[0]
				print 4
				bot.message(user, channel, request + " was last seen " + fix_time(time_diff) + " ago, " + info[1])
				print 5
				break
			else:
				print 2
				time_diff = fix_time(time.time() - bot.channels.database[channel].nickHistory[request][1])
				bot.message(user, channel, nick + " changed name to " + bot.channels.database[channel].nickHistory[request][0] + ' ' + time_diff)
				request = bot.channels.database[channel].nickHistory[request][0]
		except:
			bot.message(user, channel, "Sorry, I don't think I know who " + request + " is.")
			break
