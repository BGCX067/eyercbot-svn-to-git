'''Information on users of Valve's Steam client.'''
# MadLibs plugin
# story = {'text': 'I %s cheese and %s', 'list':['verb','noun']}
# words = [list, of, words, generated]
# story['text']%tuple(words) will be the story with the user words
import eyercbot
import eyercbot.httplib2 as httplib2

#import logging
#log = logging.getLogger("BotLogs.plugins.steam")
import eyercbot.log as log

import datetime
import json
import xml.etree.ElementTree as etree
import urllib.parse
import urllib.request

browser = httplib2.Http('.cache')

# Bold: 

# -------
# Config
# -------

# Defines the maximum length returned
# Later this will be expanded into two options, total maximum length and length per return

HAS_CONFIG = True
CONFIG_VERSION = 2
# Wait: how long to wait (s) before checking
config = {"frequency": '*/5 * * * *', 'apikey': '0', 'servers': {'serverName': ['#mychannel']}}
steamers = {}

for nick, userO in eyercbot.users.userdb.database.items():
    if hasattr(userO, "steamID64"):
        steamers[userO] = None

def add_steam(server, user, target, message):
    '''@add steam steam_url_name, @add steam steamid: Add your steam id'''
    if not message:
        eyercbot.send('sendMsg', server, user, target, add_steam.__doc__)
        return
    userO = eyercbot.users.userdb.getUser(user)
    try:
        test = int(message)
        userO.steamID64 = message
    except:
        response, content = browser.request("http://steamcommunity.com/id/"+message+"/?xml=1")
        xml = etree.fromstring(content)
        if xml[0].text.find('not be found') > -1:
            eyercbot.send('sendMsg', server, user, target, "I was unable to identify you using that profile name.")
            return
        userO.steamID64 = xml.find('steamID64').text
    eyercbot.users.userdb.save(user.split('!')[0])
    steamers[userO] = None
    eyercbot.send('sendMsg', server, user, target, "Your steam ID has been saved.")
    
def show_steam(server, user, target, message):
    if len(message.split()):
        userO = eyercbot.users.userdb.getUser(message.split()[0])
    else:
        userO = eyercbot.users.userdb.getUser(user)
    try:
        eyercbot.send('sendMsg', server, user, target, userO.nick + " steam ID: " + str(userO.steamID64))
    except:
        if userO.nick:
            eyercbot.send('sendMsg', server, user, target, "I do not have a steam ID for " + userO.nick)
        else:
            eyercbot.send('sendMsg', server, user, target, "I do not have a steam ID for that user.")
        return
    database = get_steam(userO.steamID64)
    if 'gameextrainfo' in database:
        eyercbot.send('sendMsg', server, user, target, userO.nick + ' (aka ' + database['personaname'] + ') currently playing: ' + database['gameextrainfo'])
        steamers[userO] = database['gameextrainfo']
    else:
        steamers[userO] = None

def auto_steam(*args):
    log.info("Automatic steam update")
    for userO, game in steamers.items():
        update = False
        database = get_steam(userO.steamID64)
        if 'gameextrainfo' in database and steamers[userO] == None:
            update = True
            steamers[userO] = database['gameextrainfo']
        elif 'gameextrainfo' not in database:
            steamers[userO] = None
        elif 'gameextrainfo' in database:
            if steamers[userO] != database['gameextrainfo']:
                update = True
                steamers[userO] = database['gameextrainfo']
        if update:
            for server in eyercbot.config['plugin_config']['steam']['servers']:
                for channel in eyercbot.config['plugin_config']['steam']['servers'][server]:
                    eyercbot.send('msg', server, channel, userO.nick + " is now playing " + database['gameextrainfo'])
        

def get_steam(id):
    response, content = browser.request("http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0001/?key=" + eyercbot.config['plugin_config']['steam']['apikey'] + "&steamids=" + id)
    try:
        database = json.loads(content.decode())['response']['players']['player'][0]
    except:
        log.warning('There has been an error processing this steam account:' + id)
        log.warning(content.decode())
    return database

if 'steam' in eyercbot.config['plugin_config']:
    minute, hour, day, month, day_of_week = eyercbot.config['plugin_config']['steam']['frequency'].split(' ')
    eyercbot.scheduler.add_cron_job(auto_steam, second='0', month=month, day=day, hour=hour, minute=minute, day_of_week=day_of_week)

alias_map = {"add steam": add_steam, "show steam": show_steam}