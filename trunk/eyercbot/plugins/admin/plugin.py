"""Admin plugin"""
# Bot admin plugin. Kinda needed to do stuff
import eyercbot
import logging
import os.path
log = logging.getLogger("BotLogs.plugins.admin")
HAS_CONFIG = False

def die(server, user, target, message):
    #eyercbot.bot.ident.stop()
    #eyercbot.bot.stop(message)
    eyercbot.send('quitAll')

def reloadPlugins(server, user, target, message):
    eyercbot.send('load all plugins')
    eyercbot.send('sendMsg', server, user, target, "Plugins Reloaded")

def add_plugin(server, user, target, message):
    '''Space deliminated list on plugins to try to add.
    Determines if plugin exists
    Add to and save new config
    Reload plugins.'''
    plugins = message.split(' ')
    reboot = None
    for plugin in plugins:
        x = False
        try:
            exec('import eyercbot.plugins.' + plugin)
            x = True
        except:
            x = False
        if os.path.exists(eyercbot.config['basedir']+eyercbot.config['pluginsdir']+plugin) or os.path.exists(eyercbot.exepath + '\\plugins') or x:
            eyercbot.config['plugins'].append(plugin)
            eyercbot.saveConfig()
            # Load one at time so existing plugins wont be needlessly restarted
            reboot = eyercbot.EyeRCBot.loadPlugin(plugin)
            eyercbot.send('sendMsg', server, user, target, "Plugin " + plugin + ' added.')
        else:
            eyercbot.send('sendMsg', server, user, target, 'I do not have a plugin by that name')
    if reboot: 
        eyercbot.send('sendMsg', server, user, target, "!!!!ATTENTION!!!! There have been critical updates to config file and the bot will now shut down. Please review configuration before restarting.")
        log.critical("!!!!ATTENTION!!!! There have been critical updates to "+
            eyercbot.config["nick"] + " config file and the bot will now shut down. Please review configuration before restarting.")
        die(server, user, target, message)

def show_cron(server, user, target, message):
		eyercbot.send('sendMsg', server, user, target, str(eyercbot.scheduler.dump_jobs()))

alias_map = {"die": die, "reload plugins": reloadPlugins, 'add plugin': add_plugin, 'show cron': show_cron}