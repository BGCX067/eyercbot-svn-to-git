# Stats generator.  Right now only compatible with pisg
# '!stats' will print the url
# '!stats update' will generate new stats
'''Channel statistics plugin. !stats returns the url. !stats update will update the statistics.'''
import subprocess
import ftplib
import threading
import shutil
#import EyeRClib.scheduler as scheduler
from lib.Eyecron import Task
import yaml
import lib.diskio as diskio
import sys
import os, os.path

import string 
import os,sys


# --------------------
# Configuration
config_file = open('plugins/stats/config.yaml',  'r')
stream = config_file.read()
config_file.close()
stats_config = yaml.load(stream)

stat_channels = stats_config['stat_channels']
auto_update = stats_config['auto_update']

pisg_path = stats_config['pisg_path']
cfg_path = stats_config['cfg_path']
url = stats_config['url']
man_message = stats_config['man_message']
auto_message = stats_config['auto_message']
use_ftp = stats_config['use_ftp']
ftp_server = stats_config['ftp_server']
ftp_user = stats_config['ftp_user']
ftp_pass = stats_config['ftp_pass']
ftp_path = stats_config['ftp_path']
# Moves the generated file to another destination on the local machine
# Make sure the script has permission to write to that directory
# Non functioning
use_move = stats_config['use_move']
move_dest = stats_config['move_dest']
# --------------------

# A hack to manufature event for the auto scripter
# From irclib, handy!
class Event_hack:
    """Class representing an IRC event."""
    def __init__(self, target):
        self._target = target
    def target(self):
        """Get the event target."""
        return self._target

def load(bot):
	# Updates the bot every n seconds
	#scheduler.schedule_daily(bot.connection, 00, 00, auto, once=False) 
	#scheduler.schedule_daily(bot.connection, 06, 00, auto, once=False) 
	#scheduler.schedule_daily(bot.connection, 12, 00, auto, once=False) 
	#scheduler.schedule_daily(bot.connection, 18, 00, auto, once=False) 
	task1 = Task('Stats Midnight', '00:00:00', True,  auto,  bot)
	task2 = Task('Stats 6am', '06:00:00', True,  auto,  bot)
	task3 = Task('Stats Noon', '12:00:00', True,  auto,  bot)
	task4 = Task('Stats 6pm', '18:00:00', True,  auto,  bot)

def unload(bot):
	pass

def main(bot, user, target, msg):
	if len(msg.split()) == 1:
		bot.message(user, target, 'Channel statistics URL: ' + url + target.lstrip('#') + '.html' )
	elif len(msg.split()) == 2:
		if msg.split()[1].upper() == 'UPDATE':
			# Add ftp process
			for c in stat_channels:
				update(c + '.html', man_message, bot, c)
		if msg.split()[1].upper() == 'HELP':
			bot.message(user, target, __doc__)

def auto(bot):
	for c in stat_channels:
		update(c.lstrip('#') + '.html', auto_message, bot, c)	

def upload(file_name):
	ftp = ftplib.FTP(ftp_server, ftp_user, ftp_pass)
	ftp.cwd(ftp_path)
	#file_upload = open(file_name.lstrip('#'), 'r')
	ftp.storlines('STOR ' + file_name.lstrip('#'), open(file_name.lstrip('#')))
	ftp.quit()

def update(file_name, message, bot, channel):
	subprocess.call([pisg_path, '-co', cfg_path])
	if use_ftp == True:
		#threading.Thread(target=upload(filename)).start()
		upload(file_name)
		bot.msg(channel, message + url + file_name.lstrip('#'))
		
	if use_move == True:
		copy(file_name, move_dest)
