'''Class for user.'''

import sys
import eyercbot.EyeRCBot
import hashlib
from eyercbot import database
from eyercbot import groups

userdb = None

class User():
    '''User class. Takes the bot commander in case we need to referese bot data.'''
    def __init__(self, nick=None, group='default'):
        self.nick = nick
        self.alias = []
        self.group = group
        self.hostmasks = []
        self.registered = False
        self.password = None
        self.permissions = {'whitelist': [], 'blacklist': []}
    
    def setPassword(self, newPassword):
        '''Sets a new password for the user.'''
        self.password = hashlib.sha224(newPasswordencode("utf-8")).hexdigest()
    
    def checkPassword(self, password):
        '''Checks the user password and returns boolian on match.'''
        if self.password == hashlib.sha224(passwordencode("utf-8")).hexdigest():
            return True
        else:
            return False
    
    def checkHostmask(self, hostmask):
        '''Checks to see if the user is known by the given hostmask.'''
        if hostmask in self.hostmasks:
            return True
        else:
            return False
    
    def checkPermission(self, plugin_name, plugin_command_name):
        '''Checks to see if user can exicute a specific command.  Returns boolian.
        Default permissions loaded first, overlayed by group then individual user permissions.
        Owner group automaticly returns true.
        !plugin (no parameters) can be masked with plugin.index'''
        if self.group == 'owner': return True
        
        finalWhite = self.returnWhitelist()
        #make the decision!!
        if plugin_name.lower() + '.' + plugin_command_name in finalWhite:
            return True
        elif plugin_name.lower() in finalWhite:
            return True
        else:
            return False
        # In the event of nothing catching, we return false
        return False
    
    def register(self, user, password, group):
        '''This will register the user.'''
        self.password = hashlib.sha224(password.encode("utf-8")).hexdigest()
        self.nick = user.split('!')[0]
        self.hostmasks = [user.split('!')[1]]
        self.group = group
        self.registered = True
    
    def returnWhitelist(self):
        # If owner group we return the whole deal
        if self.group == 'owner':
            return list(eyercbot.EyeRCBot.plugins.keys())
        #    return bot.plugins.database.keys()
        # Try to import default group from the user plugin.Might need to think of alternative if this fails.
        group_black = []
        group_white = []
        user_black = []
        user_white = []
        
        # Making sets and colleting permissions
        defaultPermissions = groups.groupdb.getWhitelist("default")
        final_black = set([])
        final_white = set([])
        final_white = set(defaultPermissions)
        
        if self.group:
            group_white = set(groups.groupdb.getWhitelist(self.group))
            group_black= set(groups.groupdb.getBlacklist(self.group))
        
        user_white = set(self.permissions['whitelist'])
        user_black = set(self.permissions['blacklist'])
        
        # Here we check if there are group or user permissions and overlay them
        #group_black, group_white = seterizer(group_permissions)
        # Because the default group is only a whitelist, anything in that group blacklist on the whitelist will be removed
        for g_black in group_black:
            if g_black in final_white:
                final_white = final_white.difference([g_black])
        final_black.update(group_black)
        final_white.update(group_white)
        
        #user_black, user_white = seterizer(user_permissions)
        # Now we need to remove any user whitelist from the finalblacklist, and then any userblacklist from the final whitelist
        for u_white in user_white:
            if u_white in final_black:
                final_black = final_black.difference([u_white])
        for u_black in user_black:
            if u_black in final_white:
                final_white = final_white.difference([u_black])
        final_black.update(user_black)
        final_white.update(user_white)
        
        return final_white
    
    def setPassword(self, oldPassword, newPassword):
        '''Checks if there is an existing password, then updates password.
        Returns boolian on success/failure'''
        if self.password == None: return False
        import hashlib
        if self.password == hashlib.sha224(oldPassword).hexdigest():
            self.password = self.password = hashlib.sha224(newPassword).hexdigest()
            return True
        return False
    
    def setPermissions(self, permissions):
        '''Modifies user permissions. Accepts permissions as a list of strings'''
        new_black,  new_white = self.seterizer(permissions)
        final_white = set(self.permissions['whitelist'])
        final_black = set(self.permissions['blacklist'])
        # Now the hard part.  We need to do the following
        # Check for opposite permissions and delete them
        for n_white in new_white:
            if n_white in final_black:
                final_black = final_black.difference([n_white])
        for n_black in new_black:
            if n_black in final_white:
                final_white = final_white.difference([n_black])
        # Apply the new permissions
        final_black.update(new_black)
        final_white.update(new_white)
        # Save the user file
        self.permissions['whitelist'] = list(final_white)
        self.permissions['blacklist'] = list(final_black)
    
    def seterizer(self, list):
        '''generates two sets
        one set contains all items in list that start with "-"
        the other set contains all other items'''
        black = set([])
        white = set([])
        if list[0] != '':
            for item in list:
                if item[0] == '-':
                    black.add(item[1:])
                else:
                    white.add(item.replace('+', ''))
        return black, white


class UserDatabase(database.Database):
    '''Database with additional functions common for the user database.'''
    def findHostmask(self, hostmask):
        '''Finds user entry with that hostmask and returns that object, or None.'''
        for entry in self.database:
            if hostmask in self.database[entry.lower()].hostmasks:
                return self.database[entry.lower()]
        return None
    
    def getUser(self, user):
        '''
        Returns user object from database
        Search protocol:
        1) See if name exists and then verifies hostmask, return object
        2) Scan entire database for hostmask, return object
        3) Returns a blank user object. The object is added to the database.'''
        userObject = None
        hostmask = ""
        if "!" in user:
            nick, hostmask = user.split("!")
        else:
            nick = user
        # Check to see if user name and hostmask match
        if nick.lower() in self.database:
            if self.database[nick.lower()].checkHostmask(hostmask):
                userObject = self.database[nick.lower()]
        # If not we scan the whole database for them
        if hostmask and not userObject:
            userObject = self.findHostmask(hostmask)
        # If we do not know them then we make them up
        if userObject == None:
            self.makeEntry(nick.lower())
            self.database[nick.lower()].hostmasks.append(hostmask)
            userObject = self.database[nick.lower()]
        return userObject
    
    def checkPermission(self, user, plugin, function):
        '''Command to check if the user can use a command.
        1) Check to see if the user is in the user database by name, then hostmask
        2) If no user found, then we create new temporary User object
        3) Temp or real user object then processes permissions.
        '''
        userObject = self.getUser(user)
        # We hand off checking to that object and return boolian
        return userObject.checkPermission(plugin, function)
    
    def get_whitelist(self, user):
        '''Returns whitelist of user'''
        userObject = self.getUser(user)
        return userObject.returnWhitelist()

def makeDatabase(path):
    global userdb
    userdb = UserDatabase(User, path)