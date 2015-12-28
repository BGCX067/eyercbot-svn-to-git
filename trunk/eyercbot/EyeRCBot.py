"""
Main Bot Logic. Manages plugins and higher level processing.
"""
import imp
import inspect
import sys
import time

import eyercbot
import eyercbot.log as log
import eyercbot.plugins

# Nick of the bot on the server
botnick = ''
# Map of loaded plugins
plugins = {}

# Bot specific functions, such as plugin management
def managePluginConfig(plugin_name, config, config_version):
    '''This function has the very complicated task on managing and updating the main config with the plugin config.
    The goal is to preserve user config in the event of a plugin config update.
    Plugin config version requires a bot config version of equal or greater value.
    Less than means the config must be updated.
    Returns if bot needs reboot or not
    TODO: Does not update nexted config expansions. Find a better way?
    '''
    # Step 1: Check for config in db and add if not
    if plugin_name.lower() not in list(eyercbot.config['plugin_config'].keys()):
        eyercbot.config['plugin_config'][plugin_name] = config
        eyercbot.config['plugin_config'][plugin_name]["version"] = config_version
        return True
    # Step 2: Check for version mismatch, if not then we do not need to update
    if config_version > eyercbot.config['plugin_config'][plugin_name]["version"]:
        log.critical(plugin_name + ": !!!!ATTENTION!!!! Plugin version less than config version. Fix version mismatch before restarting bot!")
        #self.stop('!!!!ATTENTION!!!! Plugin version less than config version. Fix version mismatch before restarting bot!')
    if config_version == eyercbot.config['plugin_config'][plugin_name]["version"]:
        return False
    # Step 3: Iterate though config and see if we added anything
    plugin_keys = list(config.keys())
    plugin_keys2 = plugin_keys
    for key in plugin_keys:
        if key in eyercbot.config['plugin_config'][plugin_name]:
            plugin_keys2.pop(plugin_keys2.index(key))
        else:
            eyercbot.config['plugin_config'][plugin_name][key] = config[key]
    if plugin_keys2:
        log.warning(plugin_name + ": The following plugin config were not updated. Please compare between bot config file and plugin documentation to verify syntax did not change.")
        log.warning(plugin_name + str(plugin_keys2))
    # Step 4: Find depriciated keys
    difference = set(list(config.keys())) - set(plugin_keys)
    if difference:
        log.warning(plugin_name + ": The following plugin config keys are now depriciated. Please manually remove them from the bot config file.")
        log.warning(plugin_name + str(difference))
    eyercbot.config['plugin_config'][plugin_name]["version"] = config_version
    return True

def loadPlugin(plugin_name):        
    try:
        # Loading system plugins
        filepath, pathname, description = imp.find_module(plugin_name, eyercbot.plugins.__path__)
        moduleSource = pathname +'/plugin.py'
        moduleSource = moduleSource.replace ( '\\', '/' )
        handle = open ( moduleSource )
        module = imp.load_module ( plugin_name, handle, ( moduleSource ), ( '.py', 'r', imp.PY_SOURCE ) )
        # This batch of code will be good for loading plugins in the user directory (which will happen after main ones)
        #moduleSource = 'plugins/'+plugin_name+'/plugin.py'
        #name = moduleSource.replace ( '.py', '' ).replace ( '\\', '/' ).split ( '/' ) [ 1 ]
        #handle = open ( moduleSource )
        #module = imp.load_module ( name, handle, ( moduleSource ), ( '.py', 'r', imp.PY_SOURCE ) )
        
        # Populate the main database
        plugins[plugin_name.lower()] = module
        if hasattr(module, 'alias_map'):
            for alias, function in module.alias_map.items():
                # Sometimes function may be a dict with function and threaded
                # We must check for this
                if type(function) is not dict:
                    eyercbot.messenger.add(alias, function)
                else:
                    eyercbot.messenger.add(alias, function['function'], threaded=function['threaded'])
                
        if hasattr(module, 'event_map'):
            for alias, function in module.event_map.items():
                # Sometimes function may be a dict with function and threaded
                if type(function) is not dict:
                    eyercbot.messenger.add(alias, function)
                else:
                    eyercbot.messenger.add(alias, function['function'], threaded=function['threaded'])
        
        reboot = None
        # Will now check and update configs as needed
        if module.HAS_CONFIG:        
            reboot = managePluginConfig(plugin_name, module.config, module.CONFIG_VERSION)
            if reboot: eyercbot.saveConfig()
        log.info("Plugin",plugin_name,"loaded.")
        return reboot
    except:
        log.warning("I couldn't load",plugin_name + '. I placed a report in errlog.txt for you.')
        import traceback
        traceback.print_exc(file=open("errlog.txt","a"))
        return None

def unload_plugin(plugin):
    '''Unloads target plugins, removes maps from the messenger.'''
    if hasattr(plugins[plugin], 'alias_map'):
        for alias, function in plugins[plugin].alias_map.items():
            eyercbot.messenger.delete(alias, function)
    if hasattr(plugins[plugin], 'event_map'):
        for event in plugins[plugin].event_map.items():
            eyercbot.messenger.delete(event, function)
    del plugins[plugin]

def loadAllPlugins():
    # Unloading anythign we have
    # Inhibit the dynamic view to allow mutability during iteration
    for plugin in list(plugins.keys()):
        unload_plugin(plugin)
    stop = False
    for plugin_name in eyercbot.config['plugins']:
        if loadPlugin(plugin_name):
            stop = True
    if stop:
        eyercbot.send('quitAll', "!!!!ATTENTION!!!! There have been critical updates to " +  
                eyercbot.config["nick"] + " config file and the bot will now shut down. Please review configuration before restarting.")
eyercbot.messenger.add('load all plugins', loadAllPlugins)

#
# Active bot events, like sending a message
#

def help(server, user, target, msg):
    '''Returns information on help. This will probably need to be in its own plugin eventually'''
    if not msg:
        message = "EyeRCBot Version " + str(eyercbot.VERSION) + ". Help system."
        eyercbot.send('sendMsg', server, user, target, message)
        message = "Commands begin with: " + eyercbot.config['servers'][server]["command"]
        eyercbot.send('sendMsg', server, user, target, message)
        eyercbot.send('sendMsg', server, user, target, 'Please report bugs to: http://code.google.com/p/eyercbot/issues/list')
        message = "You have access to the following plugins: "
        whitelist = eyercbot.users.userdb.get_whitelist(user)
        alias = []
        for wl in whitelist:
            if '.' in wl:
                plugin, function_name = wl.split('.')
                if plugin in plugins:
                    if hasattr(plugins[plugin], 'alias_map') and hasattr(plugins[plugin], function_name):
                        for alias, function in plugins[plugin].alias_map.items():
                            if function.__name__ == function_name:
                                message = message + alias + ", "
            else:
                if wl in plugins:
                    if hasattr(plugins[wl], 'alias_map'):
                        for alias in plugins[wl].alias_map:
                            message = message + alias + ", "
        eyercbot.send('sendMsg', server, user, target, message[:-2])
        message = "Use " + eyercbot.config['servers'][server]["command"] + "help commandname for additional help on a specific command."
        eyercbot.send('sendMsg', server, user, target, message)
        return
    else:
        for plugin in plugins:
            if hasattr(plugins[plugin], 'alias_map'):
                if msg.lower() in plugins[plugin].alias_map:
                    help_message = plugins[plugin].alias_map[msg].__doc__
                    if not help_message:
                        help_message = ' I do not have help  for that command. Please bug the administrator.'
                    eyercbot.send('sendMsg', server, user, target, help_message)
        return
    message = "No plugin found with that name."
    eyercbot.send('sendMsg', server, user, target, message)

def message(server, user, target, msg):
    '''Message logic to determine how to send response based on query (prv vs pub)
    Use msg() or notice() to overide this behavior.'''
    if target.lower() == eyercbot.config['nick'].lower():
        # Get by pm, respond by pm
        #self.msg(user.split('!')[0], msg[0:eyercbot.config['length']])
        target = user.split('!')[0]
    else:
        # Get by public, respond by public
        rep = 'awesomepants'
        msg = msg.lower().replace('bitch', rep)
        msg = msg.lower().replace('faggot', rep)
        msg = msg.lower().replace('fag', rep)
        msg = msg.lower().replace('fuck', rep)
        msg = msg.lower().replace('shit', rep)
        msg = msg.lower().replace('nigger', rep)
        msg = msg.lower().replace('cunt', rep)
    
    lines = 0
    for x in range(int(len(msg)/eyercbot.config['length'])+1):
        message = msg[lines:lines+eyercbot.config['length']]
        if not len(message):
            return
        eyercbot.send('msg', server, target, message)
        time.sleep(0.5)
        lines += eyercbot.config['length']
eyercbot.messenger.add('sendMsg', message)    

# Receptive IRC Event Related Functions
def processMsg(server, user, target, message):
    """Processes an incomming command message from a pm or in channel into plugin."""
    # Strip the command code as there is no real point is there
    message = message[1:]
    # Temporary until an admin plugin is in place
    if message.startswith("help"):
        help(server, user, target, message[5:])
        return
    # Check to see if command is a command
    # This is sucky as we have to iterate through every plugin and every alias list
    # This should be profiled at some point
    # Everything dropped to lower case just in case
    # Matching alias put here, longest one will be used
    alias_match={}
    for plugin in plugins:
        if hasattr(plugins[plugin], 'alias_map'):
            for alias in plugins[plugin].alias_map:
                if message.lower().startswith(alias.lower()):
                    alias_match[alias.lower()] =  plugin
    if not alias_match:
        log.debug("No command found: " + message)
        eyercbot.send('sendMsg', server, user, target, "I have no command by that name")
        return
    #print(alias_match)
    try:
        alias = max(alias_match)
    except:
        log.critical("Critical error parsing command")
        log.critical("Alias match: " + str(alias_match))
        log.critical("Message: " + message)
    plugin = alias_match[alias]
    function = plugins[plugin].alias_map[alias]
    
    # Test permissions
    if eyercbot.users.userdb.checkPermission(user, plugin, function.__name__):
        msg = message[len(alias):].lstrip()
        eyercbot.send(alias, server, user, target, msg)
        #print("Sending command", alias)
        #print(eyercbot.messenger.db)
    else:
        eyercbot.send('sendMsg', server, user, target, "You are not authorized for this command.")
#eyercbot.messenger.add('onMsg', processMsg)

def joined(server, nick, host, channel):
    """
    Called when someone joins a channel
    """
    if nick == botnick:
        eyercbot.send('onBotJoin', server, channel)
    else:
        eyercbot.send('onUserJoin', server, nick, channel)
eyercbot.messenger.add('onJoin', joined)

def nick_list(server, channel, nicks):
    """
    List of nicks in channel when client joins.
    May be called several times for large channels
    """
    pass

def privmsg(server, sender, target, message):
    """
    Called when bot gets a message. Seperates channel or pm logic.
    """
    if message.startswith("ACTION"):
        eyercbot.send('onAction', server, sender, target, message.lstrip("ACTION").rstrip(''))
        return
    # Call the all chat function, useful for things like logs
    eyercbot.send('allmsg', server, sender, target, message)
    # Call if private message
    if target.lower() == botnick.lower():
        # Very specific case. If we have no users, then new bot and I need user password!
        if not eyercbot.users.database and message.split()[0].startswith('password'):
            newuser(server, sender, message)
            # Return to prevent password from being logged
            return
        eyercbot.send('onPrivmsg', server, sender, message)
    else:
        eyercbot.send('onPubmsg', server, sender, target, message)
    if message.startswith(eyercbot.config['servers'][server]['command']):
        processMsg(server, sender, target, message)
eyercbot.messenger.add('onMsg', privmsg)


def signed_on(server, nick, message):
    """
    Called after sucessfully signed into the server
    """
    # Join designated channels
    global botnick
    botnick = nick
    for channel in eyercbot.config['servers'][server]['channels']:
        eyercbot.send('join channel', server, channel)
        message = "EyeRCBot Version " + str(eyercbot.VERSION) + ". Python version: " + str(sys.version)
        eyercbot.send('msg', server, channel, message)
        message = "The following plugins have been loaded: "
        for name in plugins.keys():
            message = message + name + ", "
        eyercbot.send('msg', server, channel, message[:-2])
        message = "Commands begin with " + eyercbot.config['servers'][server]["command"] + '. ' + eyercbot.config['servers'][server]["command"] + 'help to begin.'
        eyercbot.send('msg', server, channel, message)
eyercbot.messenger.add('signed on', signed_on)


# Special One shot functions that should relly only be called once
def newuser(server, user, msg):
    '''First user to PM their password will be registered as owner'''
    user_name = user.split('!')[0]
    eyercbot.users.userdb.makeEntry(user_name)
    eyercbot.users.userdb.database[user_name].register(user, msg.split()[1], 'owner')
    # We now write the new user file
    eyercbot.users.userdb.save(user_name)
    eyercbot.send('msg', server, user_name, 'You have been registered as my owner')

class StreamTee:
    """Intercept a stream.
    
    Invoke like so:
    sys.stdout = StreamTee(sys.stdout)
    
    See: grid 109 for notes on older version (StdoutTee).
    """
    def __init__(self, target):
        self.target = target
    def write(self, s):
        s = self.intercept(s)
        self.target.write(s)
    def intercept(self, s):
        """Pass-through -- Overload this."""
        return s
  
 
class SafeStreamFilter(StreamTee):
    """Convert string traffic to to something safe."""
    def __init__(self, target):
        StreamTee.__init__(self, target)
        self.encoding = 'utf-8'
        self.errors = 'replace'
        self.encode_to = self.target.encoding
    def intercept(self, s):
        return s.encode(self.encode_to, self.errors).decode(self.encode_to)

sys.stdout = SafeStreamFilter(sys.stdout)