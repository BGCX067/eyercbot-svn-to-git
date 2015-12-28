# Stats generator.  Right now only compatible with pisg
# '!stats' will print the url
# '!stats update' will generate new stats

import subprocess
import ftplib
import threading
import shutil
import sys
sys.path.append('lib')
import scheduler

stat_channels = ['MyChannel',]
auto_update = True

# Trailing slash for any option that doesn't point to a file
pisg_path = '/usr/bin/pisg'
cfg_path = '/path/to/pisg.cfg'
url = 'http://mystatssite.com/'
man_message = 'Channel stats manually updated :: '
auto_message = 'Channel stats automatically updated :: '
use_ftp = True
ftp_server = 'ftp.mystatssite.com'
ftp_user = 'username'
ftp_pass = 'password'
ftp_path = 'public_html/'
# Moves the generated file to another destination on the local machine
# Make sure the script has permission to write to that directory
# Non functioning
use_move = False
move_dest = ''

# A hack to manufature event for the auto scripter
# From irclib, handy!
class Event_hack:
    """Class representing an IRC event."""
    def __init__(self, target):

        self._target = target

    def target(self):
        """Get the event target."""
        return self._target

def on_load(connection):
	# Updates the bot every n seconds
	scheduler.schedule(connection, 21600, auto, once=True) 

def on_unload(connection, event):
	pass

def index (connection, event, channels):
	if len(event.arguments()[0].split()) == 1:
		connection.privmsg(event.target(), 'Channel statistics URL: ' + url)# Gotta find a way to get filenames in here
	elif len(event.arguments()[0].split()) == 2:
		if event.arguments()[0].split()[1].upper() == 'UPDATE':
			# Add ftp process
			for c in stat_channels:
				update(c + '.html', man_message, connection, event)
		if event.arguments()[0].split()[1].upper() == 'HELP':
			connection.privmsg(event.target(), 'Channel statistics plugin. !stats returns the url. !stats update will update the statistics.')

def auto(connection):
	for c in stat_channels:
		temp_event = Event_hack('#' + c)
		print temp_event.target()
		update(c + '.html', auto_message, connection, temp_event)	

def upload(file_name):
	ftp = ftplib.FTP(ftp_server, ftp_user, ftp_pass)
	ftp.cwd(ftp_path)
	file_upload = open(file_name, 'r')
	ftp.storlines('STOR ' + file_name, open(file_name))
	ftp.quit()

def update(file_name, message, connection, event):
	subprocess.call([pisg_path, '-co', cfg_path])
	if use_ftp == True:
		#threading.Thread(target=upload(filename)).start()
		upload(file_name)
		connection.privmsg(event.target(), message + url + file_name)
	if use_move == True:
		copy(file_name, move_dest)
