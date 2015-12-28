'''Logs channels. No commands as this is a passive plugin.'''

#import EyeRClib.scheduler as scheduler
#from eyercbot import EyeRCBot
import eyercbot
import time
import re
import datetime
import os
#import log

import logging
log = logging.getLogger("BotLogs.channel_logger")

HAS_CONFIG = True
# Config version must be at least this, otherwise upgrade!
CONFIG_VERSION = 2
config = {"channels": [], 'path': 'logs/', 'utcdif': 0}
channels = []
        
def eggLog(content, channel):
    '''Write the string to the proper log file.'''
    # IRC chan not case sensitive, we may want to lowercase if we still get odd capitalizations
    if channel not in eyercbot.config['plugin_config']['channel_logger']['channels']:
        return
    eggLogFile = open(eyercbot.config['plugin_config']['channel_logger']['path'] + channel.split('#')[1].lower() + time.strftime('.log.%Y%m%d', time.gmtime()), 'a') 
    # If the file is empty we add a midnight time stamp faking midnight.
    if os.stat(eyercbot.config['plugin_config']['channel_logger']['path'] + channel.split('#')[1].lower() + time.strftime('.log.%Y%m%d', time.gmtime()))[6] == 0:
        eggLogFile.write(time.strftime('--- %a %b %d %Y', time.gmtime()) + '\n')
    timeStamp = time.strftime('[%H:%M]', time.gmtime())
    line = timeStamp + ' ' + content
    log.info("Logged: " + line)
    eggLogFile.write(line + '\n')
    eggLogFile.close()

def action(server, user, channel, message):
    '''If a /me action is done it is written to log'''
    line = 'Action: ' + user.split('!')[0] + ' ' + message
    eggLog(line, channel)

def joined(server, user, host, channel):
    '''When someone joins the channel log and add nick to memory'''
    if user == eyercbot.config['nick']:
        line = eyercbot.config['nick'] + ' joined ' + channel + '.'
    else:
        line = user + ' (' + host + ') joined ' + channel + '.'
    eggLog(line, channel)

def modeChanged(server, user, channel, set, modes, args):
    '''Listens for a mode change then writes to log'''
    if set:
        modes = '+' + modes
    else:
        modes = '-' + modes
    try:
        line = channel + ": mode change '" + modes + ' ' + args + "' by " + user
    except:
        line = channel + ": mode change '" + modes + " ' by " + user
    eggLog(line, channel)

def publicmsg(server, user, channel, message):
    '''Channel text, write to log!'''
    eggLog('<' + user.split ('!')[0] + '> ' + message, channel)

def topic_updated(server, user, channel, new_topic):
    '''On topic changes (and first join channel)'''
    eggLog('Topic changed on ' + channel + ' by ' + user.strip('~') + ': ' + new_topic, channel)

def userKicked(server, kickee, channel, kicker, message):
    '''Reacts to kicks, logs it, and removes nick from memory'''
    line = kickee + ' kicked from ' + channel + ' by ' + kicker + ': ' + message
    eggLog(line, channel)

def userLeft (server, user, host, channel, reason):
    '''Reacts to partings, logs, and removes nick from chan memory'''
    if reason:
        line = user + ' (' + host + ') left ' + channel + ' (' + reason + ').'
    else:
        line = user + ' (' + host + ') left ' + channel + '.'
    eggLog(line, channel)

def userQuit(server, user, host, quitMessage):
    '''Reacts to partings, logs them, and removes them from channel memory'''
    for chan in channels:
        #if user.split('!')[0] in self.memory['channels'][chan]['nicks']:
        eggLog(user + ' (' + host + ') left irc: ' + quitMessage, chan)
        #    self.memory['channels'][chan]['nicks'].remove(user.split('!')[0])

def userRenamed(server, old_nick, new_nick):
    '''Listens for nick changes,  then writes to log.'''
    # We do this hack to pass to logger as I can't think of another way of passing the channel name
    for channel in eyercbot.memory[server]:
        if old_nick in eyercbot.memory[server][channel]['users']:
            eyercbot.memory[server][channel]['users'][eyercbot.memory[server][channel]['users'].index(old_nick)] = new_nick
            eggLog('Nick change: ' + old_nick + ' -> ' + new_nick, channel)

def addChannel(server, user, channel, data):
    if server not in eyercbot.bot.config['plugin_config']['channel_logger']['servers']:
        eyercbot.bot.config['plugin_config']['channel_logger']['servers'][server] = []
    eyercbot.bot.config['plugin_config']['channel_logger']['servers'][server].append(channel)
    eyercbot.bot.saveConfig()
            
# No commands as this is a passive.
alias_map = {'log channel': addChannel}
# Event maps map existing internal events (user join, parts, etc) to function
event_map = {'onAction': action, 'onJoin': joined, 'onKick': userKicked, 'onModeChange': modeChanged, 'onNick': userRenamed,  'onPart': userLeft, 'onPubmsg': publicmsg, 'onQuit': userQuit, 'onTopic': topic_updated}


