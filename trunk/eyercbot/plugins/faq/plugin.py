'''FAQ plugin.'''
# Bold: 

import os
import os.path
import eyercbot
import yaml

HAS_CONFIG = True
CONFIG_VERSION = 1
config = {"folder": 'faq/', 'filename': 'faq.yaml'}

database = {}


def add(server, user, target, message):
    '''Creates new entry. Format is @add faq key phrase, entry for key.'''
    data = message.split(', ', 1)
    if len(data) != 2:
        eyercbot.send('sendMsg', server, user, target, "Incorrect paramaters")
    elif data[0] in database.keys():
        eyercbot.send('sendMsg', server, user, target, "Key already exists, please delete first.")
    else:
        database[data[0].lower()] = data[1]
        saveDB(eyercbot.config['basedir'] + 'faq.yaml')
        eyercbot.send('sendMsg', server, user, target, data[0].lower() + " added to database.")

def list(server, user, target, message):
    '''Lists faq keys'''
    keys = 'List of topics: '
    for key in database.keys():
        keys += key + ' ,'
    eyercbot.send('msg', server, user, target, keys.rstrip(' ,'))

def search(server, user, target, message):
    '''Searches for a word or phrase.'''
    matches = set()
    for topic, entry in database.items():
        if message.lower() in topic.lower() or message.lower() in entry.lower():
            matches.add(topic)
    if not matches:
        eyercbot.send('sendMsg', server, user, target, "No match found")
    else:
        message = ''
        for entry in matches:
            message += entry + ', '
        eyercbot.send('sendMsg', server, user, target, "Matches: " + message[:-2])

def faq(server, user, target, message):
    '''Posts entry from database'''
    if message.lower() in database:
        eyercbot.send('sendMsg', server, user, target, message.lower() + ': ' + database[message.lower()])
    else:
        eyercbot.send('sendMsg', server, user, target, "There is no entry with that key in the database.")

def delete(server, user, target, message):
    if message.lower() in database:
        del database[message.lower()]
        eyercboot.send('sendMsg', server, user, target, message + ' deleted.')
        saveDB(eyercbot.config['basedir'] + 'faq.yaml')
    else:
        eyercbot.send('sendMsg', server, user, target, "There is no entry with that key in the database.")

def saveDB(path):
    stream = open(path, 'w')
    yaml.dump(database, stream)
    stream.close()
    #log.info("Configuration saved")

def loadDB(path):
    try:
        global database
        stream = open(path)
        database = yaml.load(stream)
        stream.close()
    except:
        pass

if 'faq' in eyercbot.config['plugin_config']:
    if not os.path.exists(eyercbot.config['basedir']+eyercbot.config['plugin_config']['faq']['folder']):
        os.mkdir(eyercbot.config['basedir']+eyercbot.config['plugin_config']['faq']['folder'])
    loadDB(eyercbot.config['basedir']+eyercbot.config['plugin_config']['faq']['folder'] + eyercbot.config['plugin_config']['faq']['filename'])

# The function maps the function to the input
# These need to be unique names, otherwise undesired plugin may be called!
alias_map = {"add faq": add, "search faq": search, "list faq": list, 'faq': faq, 'delete faq': delete, 'del faq': delete}