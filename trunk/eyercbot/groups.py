'''Class for user.'''

import glob
import yaml
import eyercbot.EyeRCBot
import hashlib
import eyercbot.database as database

groupdb = None

class Group(object):
    '''User class. Takes the bot commander in case we need to referese bot data.'''
    def __init__(self, name=None, whitelist=[], blacklist=[]):
        self.name = name
        self.whitelist = whitelist
        self.blacklist = blacklist


class GroupDatabase(database.Database):
    '''Database with additional functions common for the group database.'''
    def getBlacklist(self, group_name):
        return self.database[group_name]['blacklist']
    
    def getGroup(self, group_name):
        '''
        Returns group object from database.'''
        return self.database[group_name]
    
    def getWhitelist(self, group_name):
        return self.database[group_name]['whitelist']

def makeDatabase(path):
    global groupdb
    groupdb = GroupDatabase(Group, path)