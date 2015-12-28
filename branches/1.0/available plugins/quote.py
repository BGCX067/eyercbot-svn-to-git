# Quotes script
# Stores quotes in the user file in a list 
# user_list[user_name]['quotes'] = [[Submitter, Quote, [optional, tags, for, search], [Submitter, Quote, [optional, tags, for, search]]

# MUST MAKE SURE USER PLUGIN DOES NOT OVERWRITE QUOTES WHEN REGISTERING OR ANY DISK WRITE

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

import EyeRCbot
import glob
import random
import yaml

# May be able to get away with not using this
quotes_dict = {}

def on_load(connection):
	pass

def on_unload(connection, event):
	save_quotes()

def index(connection, event, channels):
	if len(event.arguments()[0].split()) == 1:
		connection.privmsg(event.target(), 'Quote script plugin. !quote add nick:nickname tags:tag1,tag2 quote:line to be quoted will add the quote to the user.  Tags are optional parameters for searching purposes.')
		return None

	if event.arguments()[0].split()[1].upper() == 'HELP':
		connection.privmsg(event.target(), 'Quote script plugin. !quote add nick:nickname tags:tag1,tag2 quote:line to be quoted will add the quote to the user.  Tags are optional parameters for searching purposes.')

	if event.arguments()[0].split()[1].upper() == 'ADD':
		if len(event.arguments()[0].split()) == 2 or len(event.arguments()[0].split()):
			connection.privmsg(event.target(), 'Quote script plugin. !quote add nick:nickname tags:tag1,tag2 quote:line to be quoted will add the quote to the user.  Tags are optional parameters for searching purposes.')
		# We make sure the user has AT LEAST nick:nick and quote:quote
		if event.arguments()[0].find('nick:') != -1 and event.arguments()[0].find('quote:') != -1:
			add_quote(connection, event)
		else:
			connection.privmsg(event.target(), 'Quote script plugin. !quote add nick:nickname tags:tag1,tag2 quote:line to be quoted will add the quote to the user.  Tags are optional parameters for searching purposes.')
	
	# Logic for pulling a random quote	
	if event.arguments()[0].split()[1].upper() == 'RANDOM' or event.arguments()[0].split()[1].upper() == 'RAND':
		user_nick2 = None
		quote_sub2 = None
		quote_tags2 = None
		quote_number2 = None
		param2 = 'rand'
		if event.arguments()[0].find('nick:') != -1:
			for word in event.arguments()[0].split():
				if word.find('nick:') != -1:
					user_nick2 = word.replace('nick:' , '')
		if event.arguments()[0].find('tags:') != -1:
			for word in event.arguments()[0].split():
				if word.find('tags:') != -1:
					pass
		quote_entry = get_quote(connection, event, user_nick = user_nick2, quote_sub = quote_sub2, quote_tags = quote_tags2, quote_number = quote_number2, param = param2)
		connection.privmsg(event.target(), quote_entry)
		

def save_quotes(user='ALL'):
	if user == 'ALL':
		for user_name in EyeRCbot.bot.user_list:
			stream = file(path_users + user_name + '.yaml', 'w')
			yaml.dump(EyeRCbot.bot.user_list[user_name], stream)
			stream.close()
	else:
		stream = file(path_users + user + '.yaml', 'w')
		yaml.dump(EyeRCbot.bot.user_list[user], stream)
		stream.close()

def add_quote(connection, event):
	# We process the nick and quote
	quote_string = quote_string_search = event.arguments()[0].replace('!quote add ','')
	for word in quote_string_search.split():
		if word.find('nick:') != -1:
			quote_nick = word.replace('nick:' , '')
			quote_string = quote_string.replace(word, '') 
		# We then process out the tags, if any
		quote_tags = None
		if event.arguments()[0].find('tags:') != -1:
			for word in event.arguments()[0].split():
				if word.find('tags:') != -1:
					quote_tags = word.replace('tags:', '').split(',')
					quote_string = quote_string.replace(word, '')
		if word.find('quote:') != -1:
			#quote_quote = word.replace('quote:', '')
			quote_string = quote_string.replace('quote:', '').lstrip()
	# Now we identify the submitter
	quote_submitter = event.source().split('!')[0]
	print EyeRCbot.bot.user_list[quote_nick]
	if quote_tags == None:
		quote_entry = [quote_submitter, quote_string, ['']]
		print quote_entry
	else:
		quote_entry = [quote_submitter, quote_string, quote_tags]
	if EyeRCbot.bot.user_list[quote_nick].has_key('quotes') == True:
		print EyeRCbot.bot.user_list[quote_nick]
		print EyeRCbot.bot.user_list[quote_nick]['quotes']
		EyeRCbot.bot.user_list[quote_nick]['quotes'].append(quote_entry)
		print EyeRCbot.bot.user_list[quote_nick]['quotes']
	else:
		EyeRCbot.bot.user_list[quote_nick]['quotes'] = [quote_entry]
	connection.privmsg(event.target(), 'Successfully added quote for ' + quote_nick + '.')
	save_quotes(quote_nick)



def get_quote(connection, event, user_nick = None, quote_sub = None, quote_tags = None, quote_number = None, param = None):
	# We copy the user database then cut out entries with no quotes
	quote_db = EyeRCbot.bot.user_list
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
		quote_user = quote_db[quote_keys[random.randint(0,len(quote_db)-1)]]['quotes']
		quote_entry = quote_user[random.randint(0,len(quote_user)-1)]
	# Random quote from a user
	if param == 'rand' and user_nick != None and quote_sub == None and quote_tags == None and quote_number == None:
		if quote_db[user_nick].has_key('quotes') == True:
			quote_entry = quote_db[user_nick][quote_keys[random.randint(0,len(quote_user))]]
		else:
			quote_entry = 'That user has no quotes.'
	return quote_entry

	


