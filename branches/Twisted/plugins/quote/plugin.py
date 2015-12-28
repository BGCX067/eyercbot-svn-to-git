# Quotes script
# Stores quotes in the user file in a list 
# bot.user_list[user_name]['quotes'] = [[Submitter, Quote, [optional, tags, for, search], [Submitter, Quote, [optional, tags, for, search]]
'''Quote script plugin. !quote add nick:nickname tags:tag1,tag2 quote:line to be quoted will add the quote to the user.  Tags are optional parameters for searching purposes. !quote random nick:nickname will pull a random quote for that user.'''

# Features: Users can add any quote to anyone

# Desired
# Features: Users can save/delete (only) their own quotes.
#           Configurable permissions for adding/deleting quotes for other people or categories.
#           Configurable number of quotes to save (users and "categories" have seperate limits.)
#           Configurable command prefix, PRIVMSG/NOTICE, etc.
#           Logs adding/deleting quotes/categories into a "quotelog" section of the datafile.
#           Special "any" category for general, unlimited number of quotes.
#           Command to create/delete "categories" for quotes (deletes all quotes for category as well).
#           Command to list all "categories" by name.
#           Command to show quote from yourself by number or at random.
#           Command to show quote from username or category by number or at random.
#           Command to show quote randomly from entire datafile.
#           Command to show quote randomly from the "any" category.
#           Command to show all quotes for username or category (in privmsg).
#           Command to show all of your own quotes (in privmsg).
#           Command to search quote datafile by keywords/text string (results shown in privmsg).
#           Command to show statistics for all quotes in the datafile (total number of quotes, users/quotes, etc.)
#           Quotes within a user's or category's saved quotes are automatically renumbered when one line is deleted.
#           Properly handles all tcl-special chars, so quotes can contain ANY input.

# -----
# Configuration
path_users = 'users/'
# -----

import glob
import random
import yaml
import EyeRClib.diskio as diskio

def load(bot):
	pass

def unload(bot):
	#save_quotes()
	pass

def main(bot, user, target, msg):
	if len(msg.split()) == 1:
		bot.msg(user,  __doc__)
		return None

	if msg.split()[1].upper() == 'HELP':
		bot.message(user, target, __doc__)

	if msg.split()[1].upper() == 'ADD':
		if len(msg.split()) < 4:
			bot.message(user, target, __doc__)
		# We make sure the user has AT LEAST nick:nick and quote:quote
		if msg.find('nick:') != -1 and msg.find('quote:') != -1:
			add_quote(bot, user, target, msg)
		else:
			bot.message(user, target, __doc__)
	
	# Logic for pulling a random quote	
	if msg.split()[1].upper() == 'RANDOM' or msg.split()[1].upper() == 'RAND':
		user_nick2 = None
		quote_sub2 = None
		quote_tags2 = None
		quote_number2 = None
		param2 = 'rand'
		if msg.find('nick:') != -1:
			for word in msg.split():
				if word.find('nick:') != -1:
					user_nick2 = word.replace('nick:' , '')
		if msg.find('tags:') != -1:
			for word in msg.split():
				if word.find('tags:') != -1:
					pass
		quote_entry = get_quote(bot, event, user_nick = user_nick2, quote_sub = quote_sub2, quote_tags = quote_tags2, quote_number = quote_number2, param = param2)
		bot.message(user, target, quote_entry)
	
	# Generate information stats
	if msg.split()[1].upper() == 'STAT' or msg.split()[1].upper() =='STATS' or msg.split()[1].upper() =='STATISTICS':
		# Print all of stats
		# We may wanna store stats in a dict entry that we compute on load and then edit directly on changes
		# This should save some cycles
		if len(msg.split()) == 2:
			quote_db = bot.users
			stats = ''
			if quote_db == {}:
				stats = 'No quotes stored'
			quote_key = quote_db.keys()
			for name in quote_key:
				if quote_db[name].has_key('quotes') == False:
					del quote_db[name]
			if quote_db == {}:
				stats = 'No quotes stored'
			for nick in quote_db:
				stats = stats + nick + ': ' + len(quote_db[nick]['quotes']) + ' '
		bot.message(user, target,  'Quote Statistics: ' + stats)

def add_quote(bot, user, target, msg):
	# We process the nick and quote
	quote_string = quote_string_search = msg.replace('!quote add ','')
	for word in quote_string_search.split():
		if word.find('nick:') != -1:
			quote_nick = word.replace('nick:' , '')
			quote_string = quote_string.replace(word, '') 
		# We then process out the tags, if any
		quote_tags = None
		if msg.find('tags:') != -1:
			for word in msg.split():
				if word.find('tags:') != -1:
					quote_tags = word.replace('tags:', '').split(',')
					quote_string = quote_string.replace(word, '')
		if word.find('quote:') != -1:
			#quote_quote = word.replace('quote:', '')
			quote_string = quote_string.replace('quote:', '').lstrip()
	# Now we identify the submitter
	quote_submitter = msg.split('!')[0]
	if quote_tags == None:
		quote_entry = [quote_submitter, quote_string, ['']]
		print quote_entry
	else:
		quote_entry = [quote_submitter, quote_string, quote_tags]
	# If the user is not in the database, we add them
	if bot.users.has_key(quote_nick) == False:
		bot.users[quote_nick] = {}
	if bot.users[quote_nick].has_key('quotes') == True:
		bot.users[quote_nick]['quotes'].append(quote_entry)
	else:
		bot.users[quote_nick]['quotes'] = [quote_entry]
	bot.message(user, target, 'Successfully added quote for ' + quote_nick + '.')
	diskio.save_user(bot, quote_nick)

def get_quote(bot, event, user_nick = None, quote_sub = None, quote_tags = None, quote_number = None, param = None):
	# We copy the user database then cut out entries with no quotes
	quote_db = bot.users
	if quote_db == {}:
		return 'No quotes stored'
	quote_key = quote_db.keys()
	for name in quote_key:
		if quote_db[name].has_key('quotes') == False:
			del quote_db[name]
	if quote_db == {}:
		return 'No quotes stored'

	# If a random quote is called with no other parameters
	if param == 'rand' and user_nick == None and quote_sub == None and quote_tags == None and quote_number == None:
		quote_keys = quote_db.keys()
		user_nick = quote_keys[random.randint(0,len(quote_db)-1)]
		quote_user = quote_db[user_nick]['quotes']
		quote_index = random.randint(0,len(quote_user)-1)
		quote_entry = format(quote_user[quote_index],  quote_index,  user_nick)
	# Random quote from a user
	if param == 'rand' and user_nick != None and quote_sub == None and quote_tags == None and quote_number == None:
		if quote_db[user_nick].has_key('quotes') == True:
			user_quotes = quote_db[user_nick]['quotes']
			quote_index = random.randint(0,len(user_quotes)-1)
			quote_entry = format(user_quotes[quote_index],  quote_index,  user_nick)
		else:
			quote_entry = 'That user has no quotes.'
	return quote_entry
	
def format(entry, entry_number,  nick):
	quote = 'Quote ' + nick + '(' + str(entry_number+1) + '): ' + entry[1] + '. Added by ' + entry[0]
	return quote
