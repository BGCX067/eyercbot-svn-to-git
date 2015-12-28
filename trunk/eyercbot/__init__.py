CONFIG_VERSION = 10
# EyeRCBot 
# Version: 3.0 series
# Written by croxis
# As is.  If it somehow removes your root directory, it isn't my fault.

# Version marker changes

# 1.0 -- Default
# 1.1 -- USER --> USERS
# 1.2 -- Plugin system now handles exceptions which are written to log without killing the whole bot
# 1.3 -- We now pass the bot instance to the plugins
# 1.4 -- More organized code. Bot responds in manner it was communicated in
# 2.0 -- Twisted library backend.  This is for AMAZEMENT!
# 3.0 -- Python 3!

# Version string: Rewrite, New core feature or plugin, New feature in plugin, Bug fix

VERSION = 3, 0, 2, 0

import inspect
import os

import yaml
from apscheduler.scheduler import Scheduler

import eyercbot.log as log
import eyercbot.messenger as messenger
import eyercbot.network as network
import eyercbot.irc as irc
import eyercbot.EyeRCBot as EyeRCBot
import eyercbot.users
import eyercbot.groups
#import eyercbot.eyecron

#config = {}
# Memory is a generic voltile memory for whatever the bot is trying to track that may span plugins.
# This is not very secure as any plugin can access it and conflicts can arise.
# If the plugin does not need to share the data, then store that information within the plugin.
memory = {}
scheduler = None
exepath = None

def send(message, *args, **kwargs):
    '''Conviance function for messenger'''
    messenger.send(message, *args, **kwargs)

def init(database):
    '''Sets up the bot!'''
    global scheduler
    global exepath
    #log.configure(database['logdir'] + database['nick'] + '.log', 'debug')
    log.configure(eyercbot.config["basedir"] + eyercbot.config["logdir"] + eyercbot.config["nick"] + ".log", eyercbot.config["logs"])
    exepath = os.path.split(inspect.getfile(inspect.currentframe()))[0]
    eyercbot.users.makeDatabase(config["userdir"])
    eyercbot.groups.makeDatabase(config["groupsdir"]) 
    #eyercbot.eyecron.makeScheduler()
    scheduler = Scheduler()
    scheduler.start()
    send('load all plugins')
    for server in database['servers']:
        send('add connection', server, database['servers'][server]['server'], database['servers'][server]['port'])
    send('connect all', database['nick'], database['nick'], database['nick'], database['nick'], database['nick'])
    send('start all')   

def saveConfig():
    stream = open(config['nick']  + '.yaml', 'w')
    yaml.dump(config, stream)
    stream.close()
    log.info("Configuration saved")

# Bot will save its memory in a yaml file for backup
def saveMemory():
    stream = file('data/' + config['nick'] +'.yaml', 'w')
    yaml.dump_all([self.memory,  self.users,  self.groups], stream)
    stream.close()

def html2irc(html):
    '''Convinace function that converts html into irc valid text'''
    import re
    html = html.replace('&middot;', '*')
    html = html.replace('<b>','')
    html = html.replace('</b>','')
    html = html.replace('<em>','')
    html = html.replace('</em>','')
    html = re.sub('<img.*?>', '',  html)
    #html = re.sub('<a.*?</a>', '', html)
    html = re.sub('<a.*?>', '', html)
    html = html.replace('</a>', '')
    html = re.sub('<sup.*?</sup>', '',  html)
    html = html.replace('<br />','')
    html = html.replace('&#39;', "'")
    html = html.replace('<i>',  '')
    html = html.replace('</i>', '' )
    html = html.replace('\x02', '')
    html = html.replace('&amp;', '&')
    html = html.replace('\xb2',  '')
    html = re.sub('<div.*?>', '',  html)
    html = html.replace('</div>',  '')
    html = html.replace('<u>',  '')
    html = html.replace('</u>',  '')
    html = html.replace('&quot;', '"')
    html = html.replace('<ul>', '')
    html = html.replace('</ul>', '')
    html = html.replace('<li>',  ' * ')
    html = html.replace('</li>',  '')
    html = re.sub('<span.*?>', '',  html)
    html = html.replace('</span>',  '')
    html = re.sub('<font.*?>', '',  html)
    html = html.replace('</font>',  '')
    html = html.replace('\n',  '')
    html = html.replace('&gt;',  '>')
    html = html.replace('&lt;',  '<')
    html = re.sub('<input.*?>', '', html)
    html = re.sub('<table.*?>', '', html)
    html = html.replace('</table>', '')
    html = html.replace('<tr>', '')
    html = html.replace('</tr>', '')
    html = re.sub('<td .*?>', '', html)
    html = html.replace('</td>', '')
    #print("HTML Conversion:", html)
    return html

def bbcode2irc(html):
    '''Converts bbcode to irc valid text'''
    import re
    html = re.sub('\[.*?\].*?\[/.*?\]','',html)
    return html