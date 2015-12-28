'''Quote script plugin. !quote random nick:nickname will pull a random quote for that user. !quote delete nick: nickname 1 will delete that number quote entry for the (optional) nick. !quote replace nick: nickname 1 New Quote will replace the quote at that entry for that nick.'''
# Quotes script
# Stores quotes in the user file in a list 
import eyercbot.users

# Features: Users can add any quote to anyone

# Desired
# Features: 
#           User can call a specific quote using nick and number index
#           Random quotes can be posted at specific intervals
#			Users can now delete quotes from self or others by index
#			Users can now replace quotes by index.
#           Users can save/delete (only) their own quotes.
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

from eyercbot.users import userdb
import eyercbot
import random

HAS_CONFIG = True
CONFIG_VERSION = 1
config = {'join_quotes': {'serverName': ['#mychannel',]}, 
    'random_quotes': {'frequency':'0 0 * * *', 'serverName': ['#mychannel',]}, 
    }


def add(server, user, target, message):
    '''add quote line to be quoted tags:tag1,tag2 will add the quote to the user.  Tags are optional parameters for searching purposes. Tags can not have spaces.'''
    nick, quote = message.split(" ", 1)
    tags = []
    if "tags:" in quote:
        quote, temp_tags = quote.split("tags")
        tags = temp_tags.split(",")
    quote_submitter = user.split("!")[0]
    quote_entry = [quote_submitter, quote, tags]
    user = eyercbot.users.userdb.getUser(nick)
    try:
        user.quotes.append(quote_entry)
    except:
        user.quotes = [quote_entry]
    eyercbot.users.userdb.save(user.nick)
    eyercbot.send('sendMsg', server, user, target, 'Successfully added quote for ' + nick + '.')

def quote(server, user, target, message):
    # We do NOT know if the user just asked for quote, or for a specific user, so we need some logic here
    print("Quote")

def join_quote(server, nick, channel):
    '''Random quote is posted if user joins that channel'''
    if server in eyercbot.config['plugin_config']['quotes']['join_quotes']:
        if channel in eyercbot.config['plugin_config']['quotes']['join_quotes'][server]:
            quotedb = makeQuoteDB()
            if nick in quotedb:
                quote_entry = getQuote(nick = nick, param = "random")
                eyercbot.send('msg', server, channel, quote_entry)

def randomQuote(server, user, target, message):
    """Calls a random quote from the quote db. An optional parameter can be given."""
    nick = None
    tag = None
    # If there is a message...
    if message:
        # Message is split as we are only passing one word
        message = message.split()[0]
        quotedb = makeQuoteDB()
        # This a user name
        if message.lower() in quotedb:
            nick = message.lower()
        else:
            tag = message.lower()
    
    quote_entry = getQuote(nick = nick, tag = tag, param = "random")
    eyercbot.send('sendMsg', server, user, target, quote_entry)

def stats(server, user, target, message):
    """Outputs quote database stats"""
    quotedb = makeQuoteDB()
    stats = ""
    if not quotedb:
        stats = "No quotes stored"
    else:
        for nick in quotedb:
            stats = stats + nick + ': ' + str(len(quotedb[nick])) + ' '
    eyercbot.send('sendMsg', server, user, target, 'Quote Statistics: ' + stats)

def makeQuoteDB():
    """Generates a special dict from the user database that only contain quotes."""
    quotedb = {}
    for user in eyercbot.users.userdb.database:
        if "quotes" in dir(eyercbot.users.userdb.database[user]):
            quotedb[user] = eyercbot.users.userdb.database[user].quotes
    return quotedb

def getQuote(nick = None, tag = None, param = None):
    # We copy the user database then cut out entries with no quotes
    quotedb = makeQuoteDB()
    if not quotedb:
        return 'No quotes stored'

    # If a random quote is called with no other parameters
    if param == 'random' and nick == None and tag == None:
        # Not friendly, anyone have a better method for getting a random key from a dict?
        nick_keys = list(quotedb.keys())
        user_nick = nick_keys[random.randint(0,len(quotedb)-1)]
        quote_list = quotedb[user_nick]
        quote_index = random.randint(0,len(quote_list)-1)
        quote_entry = format(quote_list[quote_index],  quote_index,  user_nick)
    # Random quote from a user
    elif param == 'random' and nick and not tag:
        #print("Quotedb:", quotedb)
        #print("Nick:", nick)
        if nick in quotedb:
            user_quotes = quotedb[nick]
            quote_index = random.randint(0,len(user_quotes)-1)
            quote_entry = format(user_quotes[quote_index], quote_index, nick)
        else:
            quote_entry = 'That user has no quotes.'
    return quote_entry

def format(entry, entry_number,  nick):
    quote = 'Quote ' + nick + '(' + str(entry_number+1) + '): ' + entry[1] + '. Added by ' + entry[0]
    return quote

# The function maps the function to the input
# These need to be unique names, otherwise undesired plugin may be called!
alias_map = {"add quote": add, "random quote": randomQuote, "quote stats": stats}
event_map = {'onUserJoin': join_quote}