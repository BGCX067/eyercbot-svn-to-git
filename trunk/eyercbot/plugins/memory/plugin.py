'''Plugin manages non persistant bot memory, such as channel contents. 
This is prerec for various other plugins and memory may be modified by them.'''
import eyercbot
HAS_CONFIG = False
#eyercbot.database = {}
#eyercbot.channels = {}
#eyercbot.games = {}

def setup(server, nick, messages):
    eyercbot.memory[server] = {}

def joined(server, nick, host, channel):
    if channel not in eyercbot.memory[server]:
        eyercbot.memory[server][channel] = {'users': [], 'topic': ''}
    eyercbot.memory[server][channel]['users'].append(nick)

# Disabled here as we must make sure log plugin goes first
#def nick_change(server, old_nick, new_nick):
#	for channel in eyercbot.memory[server]:
#		if old_nick in channel['users']:
#			eyercbot.memory[server][channel]['users'][eyercbot.memory[server][channel]['users'].index(old_nick)] = new_nick

def nick_list(server, channel, nicks):
    if channel not in eyercbot.memory[server]:
        joined(server, None, channel)
    for nick in nicks:
        eyercbot.memory[server][channel]['users'].append(nick.lstrip('@!+'))

def user_part(server, user, host, channel, reason):
    eyercbot.memory[server][channel]['users'].pop(eyercbot.memory[server][channel]['users'].index(user))

def topic(server, user, channel, topic):
    eyercbot.memory[server][channel]['topic'] = topic

def dump_mem(user, target, message):
    #eyercbot.bot.message(user, target, str(eyercbot.channels))
    eyercbot.bot.message(user, target, str(eyercbot.config))
    eyercbot.bot.message(user, target, str(eyercbot.memory))

# This plugin is not intended for access from IRC
#alias_map = {'dump mem': dump_mem}
event_map = {'onPart': user_part, 'onTopic': topic, 'onJoin': joined, 'signed on': setup, 'onNameReply': nick_list}
